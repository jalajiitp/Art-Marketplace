import os
import sys
import time
import requests
import random

# Add backend directory to sys.path so we can import from the main application
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
import models
import ml
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_or_create_system_user(db):
    user = db.query(models.User).filter(models.User.username == "met_museum").first()
    if not user:
        print("Creating system user 'met_museum'...")
        user = models.User(
            username="met_museum",
            email="met@example.com",
            hashed_password=pwd_context.hash("systempassword")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def main():
    print("Connecting to database...")
    db = SessionLocal()
    
    try:
        user = get_or_create_system_user(db)
        
        print("Querying Met API for public domain paintings...")
        search_url = "https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&isPublicDomain=true&q=painting"
        search_res = requests.get(search_url)
        search_res.raise_for_status()
        
        object_ids = search_res.json().get("objectIDs", [])
        if not object_ids:
            print("No objects found.")
            return
            
        print(f"Found {len(object_ids)} objects. Limiting to first 100.")
        object_ids = object_ids[:100]
        
        added_count = 0
        skipped_count = 0
        
        for obj_id in object_ids:
            time.sleep(0.1) # Rate limit handling (API allows 80 req/sec, this is safe)
            
            obj_url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{obj_id}"
            try:
                obj_res = requests.get(obj_url)
                if obj_res.status_code != 200:
                    continue
                
                data = obj_res.json()
                
                title = data.get("title")
                if not title:
                    continue
                    
                # Check if idempotent
                existing = db.query(models.Artwork).filter(models.Artwork.title == title).first()
                if existing:
                    print(f"Skipping '{title}' (already in DB)")
                    skipped_count += 1
                    continue
                    
                artist = data.get("artistDisplayName", "Unknown Artist")
                medium = data.get("medium", "")
                date = data.get("objectDate", "")
                
                # Combine into description
                description_parts = [artist]
                if date:
                    description_parts.append(date)
                if medium:
                    description_parts.append(medium)
                description = " - ".join(description_parts)
                
                image_url = data.get("primaryImage")
                if not image_url:
                    image_url = data.get("primaryImageSmall")
                
                if not image_url:
                    continue
                    
                price = round(random.uniform(500.0, 15000.0), 2)
                
                print(f"Adding '{title}'...")
                
                # Generate embedding
                text_for_embedding = f"{title} {description}"
                embedding = ml.generate_embedding(text_for_embedding)
                
                # Insert into DB
                artwork = models.Artwork(
                    title=title,
                    description=description,
                    price=price,
                    image_url=image_url,
                    embedding=embedding,
                    artist_id=user.id
                )
                
                db.add(artwork)
                db.commit()
                added_count += 1
                
            except Exception as e:
                print(f"Error processing object {obj_id}: {e}")
                db.rollback()
                
        print(f"\nSeeding complete! Added {added_count} artworks. Skipped {skipped_count} existing.")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
