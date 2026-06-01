import re
from http.server import BaseHTTPRequestHandler, HTTPServer


SENSITIVE_HEADER_RE = re.compile(
    r"(?im)^(\s*(?:(?:proxy-)?authorization|cookie|set-cookie|x-api-key|api-key))\s*:\s*(.*)$"
)
SENSITIVE_FIELD_RE = re.compile(
    r"(?i)\b([A-Za-z0-9_.-]*(?:password|passwd|pwd|token|secret|api[_-]?key)[A-Za-z0-9_.-]*)=([^&\s]+)"
)
SENSITIVE_JSON_FIELD_RE = re.compile(
    r'(?i)("?[A-Za-z0-9_.-]*(?:password|passwd|pwd|token|secret|api[_-]?key)[A-Za-z0-9_.-]*"?\s*:\s*)"([^"]*)"'
)


def redact_network_data(data):
    data = SENSITIVE_HEADER_RE.sub(r"\1: <redacted>", data)
    data = SENSITIVE_FIELD_RE.sub(r"\1=<redacted>", data)
    return SENSITIVE_JSON_FIELD_RE.sub(r'\1"<redacted>"', data)


class AutoWKNetWorkHandler(BaseHTTPRequestHandler):
    only_request = False
    only_response = True
    print_body = False

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        self.data = post_data.decode('utf-8', errors='ignore')

        if not self.only_request and not self.only_response:
            self.print_network_package(self.data)

        if self.only_request:
            self.only_listen_request(self.data)

        if self.only_response:
            self.only_listen_response(self.data)

        self.send_response(200)
        self.end_headers()

    def print_network_package(self, data):
        if self.print_body:
            print("Received Network Package:\n", redact_network_data(data))
        else:
            print("Received Network Package. Enable print_body to display redacted content.")

    def only_listen_request(self, data):
        if 'Request URL:' in data:
            self.print_network_package(data)

    def only_listen_response(self, data):
        if 'Response URL:' in data:
            self.print_network_package(data)
        if 'Request URL:' not in data and 'Response URL:' not in data:
            self.print_network_package(data)


class AutoWKListen:
    def __init__(self, server_address, print_body=False):
        self.server_address = server_address
        AutoWKNetWorkHandler.print_body = print_body
        self.server = HTTPServer(('127.0.0.1', self.server_address), AutoWKNetWorkHandler)
        print(f"AutoWK Listening on port {self.server_address}...")

    def start(self):
        self.server.serve_forever()


if __name__ == '__main__':
    al = AutoWKListen(12980)
    al.start()
