import os
import secrets
import urllib.parse

def check_envs():
    if not os.getenv('AUTH_HOSTNAME'):
        raise Exception('AUTH_HOSTNAME is not set')

def generate_random_string(length=10):
    return secrets.token_hex(length)

def get_header(request, header_name):
    return urllib.parse.unquote(request.headers.get(header_name))
