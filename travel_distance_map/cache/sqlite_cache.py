"""
SQLite cache implementation using queries as keys and responses as value.
"""
import sqlite3
from .cache import Cache

class SQLiteCache(Cache):
    def __init__(self, path, keys):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        c = self.conn.cursor()
        c.execute('''SELECT COUNT(name) FROM sqlite_master WHERE
                type ='table' AND name LIKE 'data';''')
        res = c.fetchone()
        self.keys = keys
        if not res[0]:
            c.execute('CREATE TABLE data({}, query text, response text)'.format(', '.join('{} text'.format(key) for key in self.keys)))
        self.conn.commit()

    def __contains__(self, query):
        # t = query.values
        if set(query.keys()) != set(self.keys):
            print(query.keys(), self.keys)
            raise KeyError('Query structure is different from cache')
        c = self.conn.cursor()
        c.execute('SELECT * FROM data WHERE {}'.format(' AND '.join('{} = \"{}\"'.format(key, query[key]) for key in self.keys)))
        return c.fetchone()

    def __setitem__(self, query, response):
        if query in self:
            raise KeyError("Cannot overwrite existing keys")
        c = self.conn.cursor()
        c.execute('INSERT INTO data({}) VALUES ({})'.format(','.join(self.keys + ['query', 'response']), ','.join(['\"{}\"'.format(query[key]) for key in self.keys] + ['\"{}\"'.format(str(query)), '\"{}\"'.format(response)])))
        self.conn.commit()

    def __getitem__(self, query):
        if not query in self:
            raise KeyError('Query has not been cached')
        c = self.conn.cursor()
        c.execute('SELECT response FROM data WHERE {}'.format(' AND '.join('{} = \"{}\"'.format(key, query[key]) for key in self.keys)))
        return c.fetchone()[0]

    def __del__(self):
        self.conn.close()
