from collections import namedtuple


class Cacher:
    def __init__(self, tables={}, cache_size=1000):
        self.cache_size = cache_size
        self.tables = tables
        self.init_tables()

    def __repr__(self):
        str_tables = ''
        for name in self.tables:
            str_tables = ','.join([name, str_tables])
        return '<cache.Cacher: {}>'.format(str_tables)

    def init_tables(self):
        for name, fields in self.tables.items():
            setattr(self, name, Table(name, fields))


class Table:
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields
        self.Record = namedtuple('Record', self.fields)
        self.container = []

    def __repr__(self):
        return '<cache.Table name={} size={}>'.format(self.name, len(self.container))

    def add(self, **kwargs):
        self._check_keys(kwargs)
        if not kwargs:
            return False
        line = self.Record(**kwargs)
        self.container.append(line)
        return True

    def remove(self, **kwargs):
        self._check_keys(kwargs)
        line = self.get(**kwargs)
        if line:
            self.container.remove()
            return True
        return False

    def get(self, **kwargs):
        self._check_keys(kwargs)
        match = []
        for item in self.container:
            matches = True
            for field in kwargs.keys():
                if getattr(item, field) != kwargs[field]:
                    matches = False
                    break
            if matches:
                match.append(item)
        return match

    def _check_keys(self, kwargs):
        for key in kwargs:
            if key not in self.fields:
                raise Exception('Invalid key in table.get')

if __name__ == '__main__':
    cache = Cacher(tables={'online': ('nickname', 'SSID', 'lastAct')})
    cache.online.add(SSID='sjxnask', nickname='Sasha', lastAct=10)
    cache.online.add(SSID='asxmals', nickname='Dima', lastAct=11)
    cache.online.add(SSID='asleeew', nickname='Sasha', lastAct=13)
    g = cache.online.get(nickname='Sasha')
    t = cache.online.get(SSID='asxmals')
    l = cache.online.get()
    print(cache)
    print(cache.online)
    print(g)
    print(t)
    print(l)
