from core.database.db_client import Client


class DummyClient:
    def send(*args, **kwargs):
        raise Exception('No DB client!')


DBClient = DummyClient()


def register_client(address):
    global DBClient
    DBClient = Client(address)
