from http.server import BaseHTTPRequestHandler, HTTPServer

class AutoWKNetWorkHandler(BaseHTTPRequestHandler):

    only_request=False
    only_response=True

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        self.data=post_data.decode('utf-8',errors='ignore')

        if not self.only_request and not self.only_response:
            print("Received Network Package:\n", self.data)

        if self.only_request:
            self.only_listen_request(self.data)

        if self.only_response:
            self.only_listen_response(self.data)


        self.send_response(200)
        self.end_headers()

    def only_listen_request(self,data):
        if 'Request URL:' in data:
            print("Received Network Package:\n", self.data)

    def only_listen_response(self, data):
        if 'Response URL:' in data:
            print("Received Network Package:\n", self.data)
        if 'Request URL:' not in data and 'Response URL:' not in data:
            print("Received Network Package:\n", self.data)


class AutoWKListen:
    def __init__(self, server_address):
        self.server_address = server_address
        self.server = HTTPServer(('127.0.0.1', self.server_address), AutoWKNetWorkHandler)
        print(f"AutoWK Listening on port {self.server_address}...")

    def start(self):
        self.server.serve_forever()

if __name__ == '__main__':
    al=AutoWKListen(12980)
    al.start()
