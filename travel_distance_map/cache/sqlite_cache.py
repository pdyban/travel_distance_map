"""
SQLite cache implementation using queries as keys and responses as value.
"""
import sqlite3
from .cache import Cache

class SQLiteCache(Cache):
    def __init__(self, path):
        self.path = path
        self.conn = sqlite3.connect(self.path)
        c = self.conn.cursor()
        c.execute('''SELECT COUNT(name) FROM sqlite_master WHERE
                type ='table' AND name LIKE 'data';''')
        res = c.fetchone()

        if not res[0]:
            c.execute('CREATE TABLE data(query text, response text)')
            self.keys = set()
        else:
            # reading existing Database
            c.execute('PRAGMA table_info(data)')
            self.keys = set([item[1] for item in c.fetchall() if item[1] not in ('query', 'response')])
        self.conn.commit()

    def __contains__(self, query):
        if not set(query.keys()) <= self.keys:
            return False
        c = self.conn.cursor()
        c.execute('SELECT response FROM data WHERE query LIKE ?', [query.to_json(),])
        res = c.fetchone()
        return res

    def __setitem__(self, query, response):
        if not set(query.keys()) <= self.keys:
            # append new columns
            c = self.conn.cursor()
            for key in set(query.keys()) - self.keys:
                c.execute('ALTER TABLE data ADD {}'.format(key))
                self.keys.add(key)
            self.conn.commit()
        elif query in self:
            raise KeyError("Cannot overwrite existing keys")
        c = self.conn.cursor()
        # c.execute('INSERT INTO data({}) VALUES ({})'.format(','.join(list(query.keys()) + ['query', 'response']), ','.join(['\"{}\"'.format(query[key]) for key in query.keys()] + ['\"{}\"'.format(str(query)), '\"{}\"'.format(response)])))
        keys = list(query.keys()) + ['query', 'response']
        values = [query[key] for key in query.keys()] + [query.to_json(), response]
        c.execute('INSERT INTO data({}) VALUES ({})'.format(','.join(keys), ','.join('?' for i in range(len(query) + 2))), values)
        self.conn.commit()

    def __getitem__(self, query):
        if not query in self:
            raise KeyError('Query has not been cached')
        c = self.conn.cursor()
        c.execute('SELECT response FROM data WHERE query LIKE ?', [query.to_json(),])
        return c.fetchone()[0]

    def __del__(self):
        self.conn.close()
