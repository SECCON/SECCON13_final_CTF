import json
import http.client
from typing import Optional

def get_state_from_cookie(cookie_header: Optional[str]) -> Optional[str]:
    return get_value_from_cookie(cookie_header, 'state')

def get_value_from_cookie(cookie_header: Optional[str], key: str) -> Optional[str]:
    if not cookie_header:
        return None

    cookies = dict(cookie.split('=', 1) for cookie in cookie_header.split('; '))
    return cookies.get(key)

def exchange_user_data(req) -> Optional[dict]:
    code = req.args.get('code')
    state = req.args.get('state')
    if not code or not state:
        return None

    if state != get_state_from_cookie(req.headers.get('Cookie')):
        return None

    conn = http.client.HTTPConnection('auth', 3000)

    conn.request('GET', f'/auth/id?code={code}&login_target=ADMIN')
    response = conn.getresponse()

    if response.status != 200:
        return None

    user_data = json.loads(response.read().decode())
    conn.close()

    return user_data
