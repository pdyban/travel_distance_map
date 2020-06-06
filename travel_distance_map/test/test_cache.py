import unittest
import os
from travel_distance_map import SQLiteCache, Query

TEST_DB_FILE = 'travel_distance_map/test/test.sqlite'


class TestSQLiteCache(unittest.TestCase):
    def setUp(self):
        self.query = Query('https://api.pavlo.com', {'key1': 'value1', 'key2': 'value2'})
        self.response = 'result'
        self.cache = SQLiteCache(TEST_DB_FILE)

    def tearDown(self):
        # os.remove(TEST_DB_FILE)
        pass

    def test_contains(self):
        self.assertFalse(self.query in self.cache)

    def test_getitem(self):
        with self.assertRaises(KeyError):
            self.cache[self.query]

    def test_setitem(self):
        self.cache[self.query] = self.response
        self.assertEqual(self.cache[self.query], self.response)


if __name__ == '__main__':
    unittest.main()
