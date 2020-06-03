import unittest
import os
from travel_distance_map import VBBAPICached, Query, SQLiteCache

TEST_DB_FILE = 'travel_distance_map/test/test_vbbapicached.sqlite'


class TestVBBAPICached(unittest.TestCase):
    def setUp(self):
        cache = SQLiteCache(TEST_DB_FILE)
        self.api = VBBAPICached(access_id='', cache=cache)

    def tearDown(self):
        os.remove(TEST_DB_FILE)

    def test_request(self):
        query = Query('https://postman-echo.com/get', {'foo1': 'bar1', 'foo2': 'bar2'})
        self.assertTrue(self.api.request(query))


if __name__ == '__main__':
    unittest.main()
