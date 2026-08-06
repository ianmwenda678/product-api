from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    price: float
    stock: int = Field(default=0)
    owner_id: int = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="products")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(SQLModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0

class ProductUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
