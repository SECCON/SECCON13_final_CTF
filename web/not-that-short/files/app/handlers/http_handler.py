from http.server import SimpleHTTPRequestHandler
import os
import urllib.parse
import json
from services.shortener import URLShortener
from models.url import URLModel
from utils.utils import generate_random_string, get_header
from utils.token import create_jwt_token
from utils.auth import exchange_user_data, is_logged_in

class URLShortenerHandler(SimpleHTTPRequestHandler):

    def do_POST(self):
        try:
            if not is_logged_in(self):
                self.send_error(401, 'Unauthorized')
                return

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            if self.path == '/shorten':
                data = json.loads(post_data.decode('utf-8'))
                
                original_url = data.get('url')
                if not original_url:
                    self.send_error(400, 'URL is required')
                    return

                short_code = data.get('short_code')

                if URLModel.short_code_exists(short_code):
                    self.send_error(400, 'Short code already exists')
                    return
                
                short_code = URLShortener.create_short_url(original_url, short_code)
                
                response = {
                    'short_code': short_code,
                    'short_url': f'https://{get_header(self, "Host")}/{short_code}',
                    'original_url': original_url
                }
                
                self.send_contents(200, {'Content-Type': 'application/json'}, json.dumps(response))
        except Exception as e:
            print(e)
            self.send_error(500, 'Internal Server Error')

    def do_GET(self):
        try:
            parsed_path = urllib.parse.urlparse(self.path)

            if parsed_path.path.startswith('/static/'):
                self.path = parsed_path.path[len('/static/'):]
                return SimpleHTTPRequestHandler.do_GET(self)
            elif parsed_path.path == '/auth/callback':
                user_data = exchange_user_data(self)
                if not user_data:
                    self.send_error(401, 'Invalid code or state')
                    return

                token = create_jwt_token(user_data)
                self.send_contents(302, {
                    'Content-Length': '0',
                    'Set-Cookie': f'jwt_token={token}; HttpOnly; SameSite=Lax; Path=/',
                    'Location': '/'
                }, '')
                return
            elif parsed_path.path != '/':
                short_code = parsed_path.path[1:]
                original_url = URLShortener.get_original_url(short_code)

                if original_url:
                    parsed_url = urllib.parse.urlparse(original_url)
                    if parsed_url.scheme != 'http' and parsed_url.scheme != 'https':
                        original_url = 'https://' + get_header(self, "Host") + '/' + parsed_url.geturl()

                    self.send_contents(302, {
                        'Content-Length': '0',
                        'Location': original_url
                    }, '')
                    return
                else:
                    self.send_error(404, 'Short URL not found')
                    return

            if not is_logged_in(self):
                state = generate_random_string(32)
                self.send_contents(302, {
                    'Content-Length': '0',
                    'Set-Cookie': f'state={state}; HttpOnly; SameSite=Lax; Path=/',
                    'Location': f'https://{os.getenv("AUTH_HOSTNAME")}/auth/login?login_target=APP&state={state}'
                }, '')
                return

            return SimpleHTTPRequestHandler.do_GET(self)
        except Exception as e:
            print(e)
            self.send_error(500, 'Internal Server Error')

    def send_security_headers(self):
        self.send_header('Content-Security-Policy', "default-src 'none'; form-action 'none'; script-src-elem 'sha256-AGjXyjxFrQZsoMhDB11IRItDa6oGZdwALkCRHUTaGhc='; style-src-elem 'self'; connect-src 'self';")
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
        self.send_header('Cross-Origin-Resource-Policy', 'same-origin')

    def send_response(self, code, message=None):
        super().send_response(code, message)
        self.send_security_headers()

    def send_contents(self, status_code, headers, body):
        self.send_response(status_code)
        for header, value in headers.items():
            self.send_header(header, value)
        self.end_headers()
        self.wfile.write(body.encode())
