from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json

test = "aaaa"
class S(BaseHTTPRequestHandler):
    blackList = []
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        print("aaaa")
        # parsed_path = urlparse.urlparse(self.path)
        self.wfile.write(self.blackList)

    def do_POST(self):
        self._set_headers()
        content_len = int(self.headers.getheader('content-length', 0))
        # content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        self.blackList.append(post_body)
        self.wfile.write(test)

    def do_HEAD(self):
        self._set_headers()

def run(server_class=HTTPServer,
        handler_class=S):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

run()