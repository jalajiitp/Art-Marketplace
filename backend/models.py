from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Like(Base):
    __tablename__ = "likes"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    artwork_id = Column(Integer, ForeignKey("artworks.id"), primary_key=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    artworks = relationship("Artwork", foreign_keys="[Artwork.artist_id]", back_populates="artist")
    acquired_artworks = relationship("Artwork", foreign_keys="[Artwork.owner_id]", back_populates="owner")
    liked_artworks = relationship("Artwork", secondary="likes", back_populates="liked_by")

class Artwork(Base):
    __tablename__ = "artworks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    embedding = Column(JSON)
    
    artist_id = Column(Integer, ForeignKey("users.id"))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    artist = relationship("User", foreign_keys=[artist_id], back_populates="artworks")
    owner = relationship("User", foreign_keys=[owner_id], back_populates="acquired_artworks")
    liked_by = relationship("User", secondary="likes", back_populates="liked_artworks")

    @property
    def likes_count(self):
        return len(self.liked_by)
