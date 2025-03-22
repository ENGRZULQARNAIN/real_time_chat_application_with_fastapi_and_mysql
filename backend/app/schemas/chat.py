from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class UserInfo(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    text: str


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: int
    sender_id: int
    room_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRoomBase(BaseModel):
    name: str


class ChatRoomCreate(ChatRoomBase):
    pass


class ChatRoom(ChatRoomBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRoomDetail(ChatRoom):
    # Users needs to be a list of IDs since that's what Room.users provides
    users: List[UserInfo] = Field(default_factory=list)
    messages: List[Message] = Field(default_factory=list)
    
    class Config:
        from_attributes = True 