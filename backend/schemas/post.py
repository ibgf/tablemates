from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional
from uuid import UUID

class PostUpdate(BaseModel):
    title: str
    content: str
    post_type: str
    image_urls: List[str]
    user_id: UUID
    location: Optional[str]
    max_participants: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    price: float
    city: Optional[str]
    country: Optional[str]
    is_active: bool

class PostCreate(BaseModel):
    title: str
    content: Optional[str]
    post_type: str
    image_urls: List[str] = []
    user_id: UUID
    location: Optional[str]
    max_participants: Optional[int]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    price: Optional[float]
    city: Optional[str]
    country: Optional[str]
    is_active: bool = False


class PostOut(BaseModel):
    id: UUID
    title: str
    content: Optional[str]
    post_type: str
    created_at: datetime
    image_urls: List[str] = []
    likes: int
    comments_count: int
    user_id: UUID
    clicks: int
    location: Optional[str]
    max_participants: Optional[int]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    price: Optional[float]
    status: str
    city: Optional[str]
    country: Optional[str]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
  
class FeedPostOut(BaseModel):
    id: UUID
    title: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    city: Optional[str]
    location: Optional[str]
    image_urls: List[str] = []
    likes: int
    created_at: datetime
    author_id: UUID = Field(..., alias="user_id")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
