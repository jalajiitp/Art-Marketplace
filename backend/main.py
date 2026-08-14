from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import numpy as np

import models
import schemas
import crud
import ml
import auth
from database import engine, get_db
from fastapi.security import OAuth2PasswordRequestForm

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="The Discovery Engine API")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve uploaded files statically
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def read_root():
    return {"message": "Welcome to The Discovery Engine API"}

@app.post("/auth/token", response_model=schemas.Token)
def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    refresh_token = auth.create_refresh_token(data={"sub": user.username})
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        max_age=auth.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/refresh", response_model=schemas.Token)
def refresh_token(request: Request, db: Session = Depends(get_db)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    try:
        payload = auth.jwt.decode(refresh_token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except auth.JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    user = crud.get_user_by_username(db, username=username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/logout")
def logout(response: Response):
    response.delete_cookie(key="refresh_token", httponly=True, samesite="lax")
    return {"message": "Logged out successfully"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user_uname = crud.get_user_by_username(db, username=user.username)
    if db_user_uname:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.post("/artworks/", response_model=schemas.Artwork)
async def create_artwork(
    title: str = Form(...), 
    price: float = Form(...), 
    description: Optional[str] = Form(None), 
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Handle image upload
    file_ext = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    image_url = f"/{UPLOAD_DIR}/{unique_filename}"
    
    artwork_data = schemas.ArtworkCreate(title=title, description=description or "", price=price)
    return crud.create_user_artwork(db=db, artwork=artwork_data, user_id=current_user.id, image_url=image_url)

@app.get("/artworks/", response_model=List[schemas.Artwork])
def read_artworks(skip: int = 0, limit: int = 100, search: Optional[str] = None, db: Session = Depends(get_db)):
    artworks = crud.get_artworks(db, skip=skip, limit=limit, search=search)
    return artworks

@app.get("/artworks/feed", response_model=List[schemas.Artwork])
def get_personalized_feed(
    skip: int = 0, 
    limit: int = 100, 
    search: Optional[str] = None, 
    db: Session = Depends(get_db),
    # Optional authentication
    request: Request = None
):
    # Try to get the current user if a token is provided
    current_user = None
    if request:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = auth.jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
                username = payload.get("sub")
                if username and payload.get("type") == "access":
                    current_user = crud.get_user_by_username(db, username=username)
            except Exception:
                pass

    if search:
        # If searching, just return the standard search results
        return crud.get_artworks(db, skip=skip, limit=limit, search=search)
        
    if current_user:
        # Personalize feed using Hybrid Recommender
        all_other = db.query(models.Artwork).all()
        recommendations = ml.get_hybrid_recommendations(current_user, all_other, n_results=limit)
        return recommendations
                
    # Fallback to standard recent feed
    return crud.get_artworks(db, skip=skip, limit=limit, search=None)

@app.post("/artworks/{artwork_id}/like")
def like_artwork(artwork_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    target_artwork = db.query(models.Artwork).filter(models.Artwork.id == artwork_id).first()
    if not target_artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
        
    like = db.query(models.Like).filter(models.Like.user_id == current_user.id, models.Like.artwork_id == artwork_id).first()
    if like:
        db.delete(like)
        db.commit()
        db.refresh(target_artwork)
        return {"message": "Unliked successfully", "likes_count": target_artwork.likes_count}
        
    new_like = models.Like(user_id=current_user.id, artwork_id=artwork_id)
    db.add(new_like)
    db.commit()
    db.refresh(target_artwork)
    return {"message": "Liked successfully", "likes_count": target_artwork.likes_count}

@app.delete("/artworks/{artwork_id}/like")
def unlike_artwork(artwork_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    like = db.query(models.Like).filter(models.Like.user_id == current_user.id, models.Like.artwork_id == artwork_id).first()
    if like:
        db.delete(like)
        db.commit()
    return {"message": "Unliked successfully"}

@app.get("/artworks/{artwork_id}/recommendations/", response_model=List[schemas.Artwork])
def get_artwork_recommendations(artwork_id: int, limit: int = 5, db: Session = Depends(get_db)):
    # 1. Get target artwork
    target_artwork = db.query(models.Artwork).filter(models.Artwork.id == artwork_id).first()
    if not target_artwork or not target_artwork.embedding:
        return []
        
    # 2. Get all other artworks
    all_artworks = db.query(models.Artwork).filter(models.Artwork.id != artwork_id).all()
    
    # 3. Compute similarities manually
    recommendations = ml.get_similar_artworks(
        target_embedding=target_artwork.embedding, 
        all_artworks=all_artworks, 
        n_results=limit
    )
    
    return recommendations

@app.post("/artworks/{artwork_id}/purchase")
def purchase_artwork(artwork_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    target_artwork = db.query(models.Artwork).filter(models.Artwork.id == artwork_id).first()
    if not target_artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")
        
    if target_artwork.owner_id is not None:
        raise HTTPException(status_code=400, detail="Artwork has already been acquired.")
        
    # Transfer ownership
    target_artwork.owner_id = current_user.id
    db.commit()
    db.refresh(target_artwork)
    
    return {"message": "Purchase successful! You have acquired the artwork."}

@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
