from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from agents.env import EnvironmentAgent
from utils import POSITIVE_CACHE_TIME, NEGATIVE_CACHE_TIME, POSITIVE_ALT_CACHE_TIME
from rate_limit import check_request


global_cache: set[str] = set()


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        rejection = check_request(self.client_address[0], self.headers)
        if rejection:
            status, body, headers = rejection
            self.send_response(status)
            self.send_header('Content-type', 'text/plain')
            for name, value in headers.items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(body.encode())
            return
        path = urlparse(self.path).path.split("/")
        print(path)
        if len(path) != 4:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.send_header(
                'Cache-Control', f's-maxage={NEGATIVE_CACHE_TIME}')
            self.end_headers()
            message = f"Invalid id in path: {path}"
            self.wfile.write(message.encode())
            return

        slug = path[3]
        result = EnvironmentAgent(slug).process(global_cache)
        if result[0] == 308:
            self.send_response(308)
            self.send_header('Location', result[1])
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET')
            self.send_header(
                'Cache-Control', f's-maxage={POSITIVE_CACHE_TIME}, stale-while-revalidate={POSITIVE_ALT_CACHE_TIME}')
            self.end_headers()
            return
        else:
            self.send_response(result[0])
            self.send_header('Content-type', 'text/plain')
            self.send_header(
                'Cache-Control', f's-maxage={NEGATIVE_CACHE_TIME}')
            self.end_headers()
            self.wfile.write(result[1].encode())
            return
