from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import json
import re
from database import SessionLocal, engine, Base
import models, schemas, email_util, token_util

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(
        name=user.name,
        age=user.age,
        gender=user.gender,
        email=user.email,
        city=user.city,
        interests=json.dumps(user.interests)
    )
    db.add(db_user)
    db.commit()
    db_user.interests = json.loads(db_user.interests)
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    for user in users:
        user.interests = json.loads(user.interests)
    return users

@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user.interests = json.loads(user.interests)
    return user

@app.patch("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, updated_data: schemas.UserUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    print(updated_data)
    data=updated_data.dict(exclude_unset=True)
    print(data)
    for key, value in data.items():
        if key == "interests" and value is not None:
            setattr(user, key, json.dumps(value))
        elif value is not None:
            setattr(user, key, value)
        else:
            raise HTTPException(status_code=404, detail="Null value found in the request")

    db.commit()
    db.refresh(user)
    return user

@app.delete("/users/{user_id}", response_model=dict)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": f"User with ID {user_id} deleted successfully"}

@app.get("/match/{user_id}")
def match_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_interests = json.loads(user.interests)
    matching_users = db.query(models.User).filter(
        models.User.id != user.id,
        models.User.age.between(user.age - 5, user.age + 5),
        models.User.gender != user.gender
    ).all()
    matches=[]

    for match in matching_users:
        match_interests=json.loads(match.interests)
        agescore= 30-abs(user.age-match.age)*6
        interests_score= len(set(user.interests) & set(match.interests))
        location_score= 50 if user.city == match.city else 0

        total_score=agescore+interests_score+location_score
        
        matches.append({
            "id": match.id,
            "name": match.name,
            "age": match.age,
            "city": match.city,
            "interests": match_interests,
            "match_score": total_score
        })
    matches.sort(key=lambda x: x["match_score"], reverse=True)
    return matches

@app.get("/validate-email/{user_id}")
def match_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_verified:
        return {"message": f"Already Verified"}
    
    valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user.email)

    if not valid:
        raise HTTPException(status_code=404, detail="Invalid email format please update correct email")

    if not email_util.send_verification_email(user.email):
        raise HTTPException(status_code=500, detail="Error sending verification email please try again")
    
    return {"message": f"Verification Mail sent to registered email successfully"}

@app.get("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    email = token_util.verify_jwt_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.commit()
    return {"message": "Email verified successfully!"}


