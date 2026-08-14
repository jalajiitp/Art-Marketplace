from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
import schemas
import ml

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_artworks(db: Session, skip: int = 0, limit: int = 100, search: str = None):
    query = db.query(models.Artwork)
    if search:
        all_artworks = query.all()
        search_embedding = ml.generate_embedding(search)
        if search_embedding:
            # Semantic search
            return ml.get_similar_artworks(search_embedding, all_artworks, n_results=limit)
    return query.offset(skip).limit(limit).all()

def create_user_artwork(db: Session, artwork: schemas.ArtworkCreate, user_id: int, image_url: str):
    # Determine local file path from image_url
    # image_url is like /uploads/filename.jpg
    # We need the absolute path or relative path to the backend dir
    import os
    # Strip leading slash to get relative path 'uploads/filename.jpg'
    local_path = image_url.lstrip('/')
    
    # Generate embedding based on image features + text
    embedding = ml.extract_image_features(local_path, title=artwork.title, description=artwork.description or "")
    
    db_artwork = models.Artwork(**artwork.model_dump(), artist_id=user_id, image_url=image_url, embedding=embedding)
    db.add(db_artwork)
    db.commit()
    db.refresh(db_artwork)
    
    return db_artwork
