import os
from database import SessionLocal
import models
import ml
import time

def regenerate_embeddings():
    db = SessionLocal()
    artworks = db.query(models.Artwork).all()
    print(f"Found {len(artworks)} artworks to update.")
    
    count = 0
    for art in artworks:
        print(f"Updating embedding for: {art.title}")
        # text for embedding
        text_for_embedding = f"{art.title} {art.description or ''}"
        
        # We don't want to re-run the full vision API for every pre-seeded image to save API calls/time,
        # so we will just embed the text for the existing ones. New uploads will get the full vision treatment.
        new_embedding = ml.generate_embedding(text_for_embedding)
        
        if new_embedding:
            art.embedding = new_embedding
            count += 1
            
        # small delay to avoid rate limiting
        time.sleep(0.5)
            
    db.commit()
    db.close()
    print(f"Successfully updated {count} embeddings.")

if __name__ == "__main__":
    regenerate_embeddings()
