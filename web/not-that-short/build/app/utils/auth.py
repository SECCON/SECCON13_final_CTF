from utils.token import get_state_from_cookie, get_token_from_cookie
from utils.token import verify_jwt_token
from typing import Optional
import urllib.parse
import json
import http.client

def exchange_user_data(req) -> Optional[dict]:
    parsed_url = urllib.parse.urlparse(req.path)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    code = query_params.get('code', [None])[0]
    state = query_params.get('state', [None])[0]
    if not code or not state:
        return None
    
    if state != get_state_from_cookie(req.headers.get('Cookie')):
        return None

    conn = http.client.HTTPConnection('auth', 3000)
    
    conn.request('GET', f'/auth/id?code={code}&login_target=APP')
    response = conn.getresponse()
    
    if response.status != 200:
        return None

    user_data = json.loads(response.read().decode())
    conn.close()
    
    return user_data

def is_logged_in(req) -> bool:
    cookie_header = req.headers.get('Cookie')
    token = get_token_from_cookie(cookie_header)
    if not token:
        return False
        
    user_data = verify_jwt_token(token)
    return user_data is not None
