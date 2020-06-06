import unittest
import os
from travel_distance_map import VBBAPICached, Query, SQLiteCache
from travel_distance_map import GPSPoint

TEST_DB_FILE_MOCK = 'travel_distance_map/test/test_vbbapicachedmock.sqlite'
TEST_DB_FILE = 'travel_distance_map/test/test_vbbapicached.sqlite'


class TestVBBAPICachedMock(unittest.TestCase):
    def setUp(self):
        cache = SQLiteCache(TEST_DB_FILE_MOCK)
        self.api = VBBAPICached(access_id='', cache=cache)

    def tearDown(self):
        os.remove(TEST_DB_FILE_MOCK)

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

    def test_get_closest_stop(self):
        location = GPSPoint(52.5219216,13.411026)  # Berlin, Alexanderplatz
        result = self.api.get_closest_stop(location)
        self.assertEqual('S+U Alexanderplatz Bhf/Dircksenstr. (Berlin)', result.name)
        self.assertEqual('900100024', result.id)
        # should now pull result from cache and the result should be in same format as the original
        result2 = self.api.get_closest_stop(location)
        self.assertEqual(result2, result)

    def test_can_init_old_cache(self):
        cache = SQLiteCache(TEST_DB_FILE)
        with open('ACCESS_ID.txt') as f:
            ACCESS_ID = f.read().strip()
        api2 = VBBAPICached(access_id=ACCESS_ID, cache=cache)
        result = api2.get_closest_stop(GPSPoint(52.5219216,13.411026))
        self.assertEqual('900100024', result.id)


if __name__ == '__main__':
    unittest.main()
