from http.server import HTTPServer
from core.static_handler import StaticHandler


def main():
    address = (HOST, PORT) = ('', 8080)
    server = HTTPServer(address, StaticHandler)
    print('Listening on {}:{}...'.format(HOST, PORT))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer is shutting')


if __name__ == '__main__':
    main()
