import socket


class DBClient:
    def __init__(self, ipc_path):
        self.ipc_path = ipc_path

    def send(self, query):
        ipc = socket.socket(socket.AF_UNIX)
        ipc.connect(self.ipc_path)
        print('Client sending query: {}'.format(query))
        ipc.sendall(query)
        resp = ipc.recv(2048)
        if resp:
            print('Client received response: {}'.format(resp))
            return resp
        print('Client received no response')

    def create_new_user(self, username, passwd):
        request = 'NEWUSR name={}&passwd={}'.format(username, passwd)
        if self.send(request):
            return True
        return False
