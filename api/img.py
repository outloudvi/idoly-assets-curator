from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from main import get_image_url


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = urlparse(self.path).path.split("/")
        print(path)
        if len(path) != 4:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            message = f"Invalid id in path: {path}"
            self.wfile.write(message.encode())
            return

        image_url = get_image_url(path[3])
        if image_url is None:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            message = "Asset not found"
            self.wfile.write(message.encode())
            return

        self.send_response(302)
        self.send_header('Location', image_url)
        self.end_headers()
        return
