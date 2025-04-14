from flask import Flask, request, make_response, redirect
import os
from utils.auth import exchange_user_data
from utils.utils import generate_random_string

app = Flask(__name__)

FLAG = os.getenv('FLAG')

if not FLAG or not FLAG.startswith('SECCON{') or not FLAG.endswith('}'):
    print('Bad flag')
    exit(1)


def send_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'none'; form-action 'none';"
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
    return response

@app.route('/auth/callback')
def handle_callback():
    user_data = exchange_user_data(request)
    if not user_data:
        return send_security_headers(make_response('Invalid code or state', 401))

    if user_data.get('user_id') == 1 and user_data.get('username') == 'admin' and user_data.get('is_admin'):
        return send_security_headers(make_response(f'Congratulations! Here is your flag: {FLAG}'))
    else:
        return send_security_headers(make_response("You're not allowed to access this page", 401))

@app.route('/')
@app.route('/<path:path>')
def handle_default(path=''):
    state = generate_random_string(32)
    response = make_response(redirect(
        f'https://{os.getenv("AUTH_HOSTNAME")}/auth/login?login_target=ADMIN&state={state}'
    ))
    response.set_cookie('state', state, httponly=True, samesite='Lax', path='/')
    return send_security_headers(response)

@app.errorhandler(Exception)
def handle_error(e):
    print(e)
    return 'Internal Server Error', 500
