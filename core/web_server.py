from http.server import BaseHTTPRequestHandler
from socketserver import TCPServer

class MasterHandler(BaseHTTPRequestHandler):
    def handle(self):
        pass


def main():
    HOST, PORT = "localhost", 9999
    server = TCPServer((HOST, PORT), MasterHandler)
    server.serve_forever()

if __name__ == "__main__":
    main()

