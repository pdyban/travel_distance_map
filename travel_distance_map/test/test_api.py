import unittest
import os
from travel_distance_map import VBBAPICached, Query, SQLiteCache
from travel_distance_map import GPSPoint

TEST_DB_FILE = 'travel_distance_map/test/test_vbbapicachedmock.sqlite'
TEST_DB_FILE = 'travel_distance_map/test/test_vbbapicached.sqlite'


class TestVBBAPICachedMock(unittest.TestCase):
    def setUp(self):
        cache = SQLiteCache(TEST_DB_FILE)
        self.api = VBBAPICached(access_id='', cache=cache)

    def tearDown(self):
        os.remove(TEST_DB_FILE)

    def test_request(self):
        query = Query('https://postman-echo.com/get', {'foo1': 'bar1', 'foo2': 'bar2'})
        self.assertTrue(self.api.request(query))


class TestVBBAPICached(unittest.TestCase):
    def setUp(self):
        cache = SQLiteCache(TEST_DB_FILE)
        with open('ACCESS_ID.txt') as f:
            ACCESS_ID = f.read().strip()
        self.api = VBBAPICached(access_id=ACCESS_ID, cache=cache)

    def tearDown(self):
        os.remove(TEST_DB_FILE)

    def test_request(self):
        location = GPSPoint(52.5219216,13.411026)  # Berlin, Alexanderplatz
        result = self.api.get_closest_stop(location)
        self.assertEqual('S+U Alexanderplatz Bhf/Dircksenstr. (Berlin)', result['name'])
        self.assertEqual('900100024', result['extId'])


if __name__ == '__main__':
    unittest.main()
