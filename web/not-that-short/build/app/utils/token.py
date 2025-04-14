import os
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict
import secrets

JWT_SECRET = secrets.token_hex(32)
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

def create_jwt_token(user_data: Dict) -> str:
    expiration = datetime.now() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        **user_data,
        'exp': expiration
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> Optional[Dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_token_from_cookie(cookie_header: Optional[str]) -> Optional[str]:
    return get_value_from_cookie(cookie_header, 'jwt_token')

def get_state_from_cookie(cookie_header: Optional[str]) -> Optional[str]:
    return get_value_from_cookie(cookie_header, 'state')

def get_value_from_cookie(cookie_header: Optional[str], key: str) -> Optional[str]:
    if not cookie_header:
        return None
    
    cookies = dict(cookie.split('=', 1) for cookie in cookie_header.split('; '))
    return cookies.get(key)
