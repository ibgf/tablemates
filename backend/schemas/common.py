from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class LikeStatus(BaseModel):
    liked: bool


class FavoriteStatus(BaseModel):
    favorited: bool


class ToggleResponse(BaseModel):
    status: str
    action: str
    count: int
