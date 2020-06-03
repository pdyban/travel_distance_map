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
        self.keys = set()
        if not res[0]:
            c.execute('CREATE TABLE data(query text, response text)')
        self.conn.commit()

    def __contains__(self, query):
        if not set(query.keys()) <= self.keys:
            return False
        c = self.conn.cursor()
        c.execute('SELECT * FROM data WHERE {}'.format(' AND '.join('{} = \"{}\"'.format(key, query[key]) for key in query.keys())))
        return c.fetchone()

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
        c.execute('INSERT INTO data({}) VALUES ({})'.format(','.join(list(query.keys()) + ['query', 'response']), ','.join(['\"{}\"'.format(query[key]) for key in query.keys()] + ['\"{}\"'.format(str(query)), '\"{}\"'.format(response)])))
        self.conn.commit()

    def __getitem__(self, query):
        if not query in self:
            raise KeyError('Query has not been cached')
        c = self.conn.cursor()
        c.execute('SELECT response FROM data WHERE {}'.format(' AND '.join('{} = \"{}\"'.format(key, query[key]) for key in query.keys())))
        return c.fetchone()[0]

    def __del__(self):
        self.conn.close()
