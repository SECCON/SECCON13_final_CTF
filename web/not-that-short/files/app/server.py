from http.server import ThreadingHTTPServer
from handlers.http_handler import URLShortenerHandler
from config.database import init_db
from utils.utils import check_envs

def run_server(port=8000):
    check_envs()
    init_db()

    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, URLShortenerHandler)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
