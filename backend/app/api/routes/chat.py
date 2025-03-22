from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.db import get_db
from app.core.security import get_current_user
from app.models import ChatRooms, Messages, Users, RoomUsers
from app.schemas.chat import (
    ChatRoom, 
    ChatRoomCreate, 
    ChatRoomDetail,
    Message, 
    MessageCreate
)

router = APIRouter(tags=["Chat"])


@router.get("/rooms", response_model=List[ChatRoom])
async def get_chat_rooms(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """List all available chat rooms"""
    return db.query(ChatRooms).all()


@router.get("/rooms/{room_id}", response_model=ChatRoomDetail)
async def get_chat_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get specific chat room details"""
    # Get the room with its users relationship explicitly loaded
    room = db.query(ChatRooms).filter(ChatRooms.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat room not found"
        )
    
    # Return the room directly - schema will handle the conversion
    return room


@router.post("/rooms", response_model=ChatRoom)
async def create_chat_room(
    room: ChatRoomCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Create a new chat room"""
    db_room = ChatRooms(name=room.name)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    
    # Add the creator to the room
    room_user = RoomUsers(room_id=db_room.id, user_id=current_user.id)
    db.add(room_user)
    db.commit()
    
    return db_room


@router.post("/rooms/{room_id}/messages", response_model=Message)
async def create_message(
    room_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Send message to a chat room"""
    # Check if room exists
    room = db.query(ChatRooms).filter(ChatRooms.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat room not found"
        )
    
    # Check if user is in the room
    room_user = db.query(RoomUsers).filter(
        RoomUsers.room_id == room_id,
        RoomUsers.user_id == current_user.id
    ).first()
    
    if not room_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this chat room"
        )
    
    # Create message
    db_message = Messages(
        text=message.text,
        sender_id=current_user.id,
        room_id=room_id
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return db_message


@router.get("/rooms/{room_id}/messages", response_model=List[Message])
async def get_chat_history(
    room_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Get chat room message history"""
    # Check if room exists
    room = db.query(ChatRooms).filter(ChatRooms.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat room not found"
        )
    
    # Check if user is in the room
    room_user = db.query(RoomUsers).filter(
        RoomUsers.room_id == room_id,
        RoomUsers.user_id == current_user.id
    ).first()
    
    if not room_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this chat room"
        )
    
    # Get messages
    messages = db.query(Messages).filter(
        Messages.room_id == room_id
    ).order_by(desc(Messages.created_at)).limit(limit).all()
    
    return messages


@router.post("/rooms/{room_id}/join")
async def join_chat_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Join a chat room"""
    # Check if room exists
    room = db.query(ChatRooms).filter(ChatRooms.id == room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat room not found"
        )
    
    # Check if user is already in the room
    room_user = db.query(RoomUsers).filter(
        RoomUsers.room_id == room_id,
        RoomUsers.user_id == current_user.id
    ).first()
    
    if room_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this chat room"
        )
    
    # Add user to room
    room_user = RoomUsers(room_id=room_id, user_id=current_user.id)
    db.add(room_user)
    db.commit()
    
    return {"detail": "Successfully joined chat room"} 