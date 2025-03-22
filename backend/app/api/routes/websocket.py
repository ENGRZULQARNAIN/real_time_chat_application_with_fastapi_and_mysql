import json
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.core.db import get_db
from app.core.config import settings
from app.models import Users, Messages, ChatRooms, RoomUsers
from app.core.security import is_token_blacklisted

router = APIRouter(tags=["WebSocket"])

# Keep track of active connections
class ConnectionManager:
    def __init__(self):
        # Structure: {room_id: {user_id: WebSocket}}
        self.active_connections: Dict[int, Dict[int, WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, room_id: int, user_id: int, already_accepted=False):
        """Connect a WebSocket to a room"""
        # Only accept the connection if it hasn't been accepted already
        if not already_accepted:
            await websocket.accept()
            
        # Register connection
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][user_id] = websocket
        
    def disconnect(self, room_id: int, user_id: int):
        if room_id in self.active_connections:
            if user_id in self.active_connections[room_id]:
                del self.active_connections[room_id][user_id]
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                
    async def broadcast_to_room(self, room_id: int, message: dict):
        if room_id in self.active_connections:
            for user_id, connection in self.active_connections[room_id].items():
                await connection.send_json(message)
                
    def get_user_connection(
        self, room_id: int, user_id: int
    ) -> Optional[WebSocket]:
        if (room_id in self.active_connections and 
                user_id in self.active_connections[room_id]):
            return self.active_connections[room_id][user_id]
        return None
        
    def get_connected_users(self, room_id: int) -> List[int]:
        if room_id in self.active_connections:
            return list(self.active_connections[room_id].keys())
        return []


manager = ConnectionManager()


async def get_current_user_from_token(token: str, db: Session) -> Users:
    """Validate JWT token and return user"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        email: str = payload.get("sub")
        if email is None:
            return None
        if is_token_blacklisted(token):
            return None
    except JWTError:
        return None
        
    user = db.query(Users).filter(Users.email == email).first()
    return user


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    room_id: int,
    db: Session = Depends(get_db)
):
    # Extract token from query parameters
    token = None
    try:
        # Get query parameters from the URL
        query_params = dict(websocket.query_params)
        token = query_params.get("token")
        print(f"WebSocket connection request for room {room_id}")
        if token:
            print(f"Token provided with length: {len(token)}")
    except Exception as e:
        print(f"Error extracting token: {str(e)}")
        token = None
    
    # Accept the connection first (required before sending any messages)
    await websocket.accept()
    print(f"WebSocket connection accepted for room {room_id}")
    
    if not token:
        print("No token provided")
        await websocket.send_json({"error": "Authentication required"})
        await websocket.close()
        return
    
    try:    
        # Authenticate user
        user = await get_current_user_from_token(token, db)
        if not user:
            print(f"Invalid authentication token for room {room_id}")
            await websocket.send_json({"error": "Invalid authentication token"})
            await websocket.close()
            return
            
        print(f"User authenticated: {user.email} (ID: {user.id})")
            
        # Check if room exists
        room = db.query(ChatRooms).filter(ChatRooms.id == room_id).first()
        if not room:
            print(f"Room {room_id} not found")
            await websocket.send_json({"error": "Chat room not found"})
            await websocket.close()
            return
        
        # Check if user is in the room
        room_user = db.query(RoomUsers).filter(
            RoomUsers.room_id == room_id,
            RoomUsers.user_id == user.id
        ).first()
        
        if not room_user:
            print(f"User {user.id} is not a member of room {room_id}")
            await websocket.send_json({
                "error": "You are not a member of this chat room"
            })
            await websocket.close()
            return
        
        print(f"User {user.id} is authorized for room {room_id}")
        
        # Add to connection manager - note we don't need to accept again here
        # since we already accepted the connection above
        await manager.connect(websocket, room_id, user.id, already_accepted=True)
        
        # Notify room about new user
        await manager.broadcast_to_room(
            room_id,
            {
                "type": "user_joined",
                "user_id": user.id,
                "user_name": user.name,
                "room_id": room_id,
                "active_users": manager.get_connected_users(room_id)
            }
        )
        
        print(f"User {user.id} joined room {room_id} successfully")
        
        try:
            while True:
                # Wait for messages from the client
                data = await websocket.receive_text()
                message_data = json.loads(data)
                
                # Save message to database
                db_message = Messages(
                    text=message_data.get("text", ""),
                    sender_id=user.id,
                    room_id=room_id
                )
                
                db.add(db_message)
                db.commit()
                db.refresh(db_message)
                
                # Broadcast to all connected clients in the room
                await manager.broadcast_to_room(
                    room_id,
                    {
                        "type": "message",
                        "id": db_message.id,
                        "text": db_message.text,
                        "sender_id": db_message.sender_id,
                        "sender_name": user.name,
                        "room_id": db_message.room_id,
                        "created_at": db_message.created_at.isoformat()
                    }
                )
        except WebSocketDisconnect:
            print(f"WebSocket disconnected for user {user.id} in room {room_id}")
            # Remove from active connections
            manager.disconnect(room_id, user.id)
            
            # Notify room about user leaving
            await manager.broadcast_to_room(
                room_id,
                {
                    "type": "user_left",
                    "user_id": user.id,
                    "user_name": user.name,
                    "room_id": room_id,
                    "active_users": manager.get_connected_users(room_id)
                }
            )
        except Exception as e:
            print(f"Error in WebSocket handler: {str(e)}")
            # Remove from active connections
            manager.disconnect(room_id, user.id)
            
            # Notify room about user leaving
            await manager.broadcast_to_room(
                room_id,
                {
                    "type": "user_left",
                    "user_id": user.id,
                    "user_name": user.name,
                    "room_id": room_id,
                    "active_users": manager.get_connected_users(room_id)
                }
            )
    except Exception as e:
        print(f"Unhandled WebSocket error: {str(e)}")
        await websocket.close() 