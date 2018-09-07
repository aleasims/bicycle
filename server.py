import socket


BUFLEN = 1024


class Server:
    # Simple functionality realization
    # Responses '200 OK' to _any_ received msg
    # Msg ending is defined as '\r\n\r\n' (as for HTTP)
    def __init__(self, host='127.0.0.1', port=8080):
        self.addr = (self.host, self.port) = (host, port)
        self.sock = socket.socket()
        self.sock.bind(self.addr)
        self.sock.listen(1)
        print('Server binded to {}:{}'.format(self.host, self.port))

    def __del__(self):
        self.sock.close()

    def run(self):
        response = b'HTTP/1.1 200 OK'
        while True:
            print('\n\nWaiting for clients...')
            (conn, address) = self.sock.accept()
            print('Connection accepted: {}'.format(address))
            request = bytearray()
            while True:
                buf = conn.recv(BUFLEN)
                request += buf
                if b'\r\n\r\n' in request:
                    break
            print('Request received:\n{}'.format(request))
            conn.send(response)
            conn.close()
            print('Connection closed')


if __name__ == '__main__':
    Server().run()
