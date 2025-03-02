from pydantic import BaseModel, validator
import json
from typing import List,Optional

class UserBase(BaseModel):
    name: str
    age: int
    gender: str
    email: str
    city: str
    interests: List[str]
    @validator("interests", pre=True)
    def validate_interests(cls, v):
        if isinstance(v, str): 
            return json.loads(v)
        return v  


class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    interests: Optional[List[str]] = None  

class User(UserBase):
    id: int
    is_verified : bool
    class Config:
        orm_mode = True

