from database import SessionLocal, engine
import models
import crud
import schemas

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

user = crud.get_user(db, user_id=1)
if not user:
    user_data = schemas.UserCreate(
        username="artist_zero",
        email="zero@discovery.engine",
        password="securepassword"
    )
    crud.create_user(db, user_data)
    print("Seeded initial user.")
else:
    print("Initial user already exists.")

db.close()
