from pydantic import BaseModel
from typing import List, Optional
import datetime

class ArtworkBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float

class ArtworkCreate(ArtworkBase):
    pass

class Artwork(ArtworkBase):
    id: int
    image_url: str
    created_at: datetime.datetime
    artist_id: int
    owner_id: Optional[int] = None
    likes_count: int = 0

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    artworks: List[Artwork] = []
    acquired_artworks: List[Artwork] = []
    liked_artworks: List[Artwork] = []

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
