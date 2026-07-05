import os 
from datetime import datetime, timedelta, timezone

import jwt

SECRET = os.environ["JWT_SECRET"]
ALGORITHM = "HS256"
EXPIRY_MINUTES = 15

def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=EXPIRY_MINUTES),
    }
    return jwt.encode(payload, SECRET, algorithm=ALGORITHM)
