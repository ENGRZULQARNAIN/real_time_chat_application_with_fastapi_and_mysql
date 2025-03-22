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


