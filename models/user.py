from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=100)
    hashed_password: str = Field(max_length=255)
    full_name: str = Field(max_length=100)
    role: str = Field(default="user", max_length=50)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    products: List["Product"] = Relationship(back_populates="owner")

class UserCreate(SQLModel):
    username: str = Field(max_length=50)
    email: str = Field(max_length=100)
    password: str = Field(max_length=100)
    full_name: str = Field(max_length=100)
    role: str = Field(default="user", max_length=50)

class UserLogin(SQLModel):
    username: str = Field(max_length=50)
    password: str = Field(max_length=100)

class UserResponse(SQLModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
