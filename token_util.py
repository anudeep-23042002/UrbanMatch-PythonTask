import jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

#1hr expiration time
def generate_jwt_token(email: str, expires_in=3600):
    expiration = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    payload = {"email": email, "exp": expiration}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    print("Generated Token:", token)  
    return token

def verify_jwt_token(token: str):
    try:
        print("Received Token:", token)  
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("Decoded Payload:", payload)  
        return payload["email"]
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return None

