from database import SessionLocal
import crud
import models

db = SessionLocal()
a = db.query(models.Artwork).first()
if a:
    u = db.query(models.User).first()
    if not u:
        print("No user")
    else:
        like = db.query(models.Like).filter(models.Like.user_id == u.id, models.Like.artwork_id == a.id).first()
        if like:
            db.delete(like)
        else:
            new_like = models.Like(user_id=u.id, artwork_id=a.id)
            db.add(new_like)
        db.commit()
        db.refresh(a)
        print("New likes_count:", a.likes_count)
