from http.server import HTTPServer
from core.static_handler import StaticHandler
import web_server


def old_main():
    address = (HOST, PORT) = ('', 8080)
    server = HTTPServer(address, StaticHandler)
    print('Listening on {}:{}...'.format(HOST, PORT))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer is shutting')

def main():
    web_server.main()

if __name__ == '__main__':
    main()
