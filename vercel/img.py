from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from agents.img import ImageAgent


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = urlparse(self.path).path.split("/")
        print(path)
        if len(path) != 4:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET')
            self.end_headers()
            message = f"Invalid id in path: {path}"
            self.wfile.write(message.encode())
            return

        slug = path[3]
        result = ImageAgent(slug).process()
        if result[0] == 302:
            self.send_response(302)
            self.send_header('Location', result[1])
            self.end_headers()
            return
        else:
            self.send_response(result[0])
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(result[1].encode())
            return
