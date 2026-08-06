from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    price: float = Field(default=0.0)
    stock: int = Field(default=0)
    owner_id: int = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="products")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(SQLModel):
    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    price: float = Field(default=0.0, ge=0)
    stock: int = Field(default=0, ge=0)

class ProductUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=500)
    price: Optional[float] = Field(default=None, ge=0)
    stock: Optional[int] = Field(default=None, ge=0)
