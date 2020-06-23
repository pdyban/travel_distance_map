import unittest
import os
from datetime import datetime
from travel_distance_map import VBBAPICached, APICached, Query, SQLiteCache
from travel_distance_map import GPSPoint, Position
from travel_distance_map import Trip

TEST_DB_FILE_MOCK = 'travel_distance_map/test/test_apicached.sqlite'
TEST_DB_FILE = 'travel_distance_map/test/test_vbbapicached.sqlite'


class TestAPICached(unittest.TestCase):
    def setUp(self):
        cache = SQLiteCache(TEST_DB_FILE_MOCK)
        self.api = APICached(cache=cache)

    def tearDown(self):
        os.remove(TEST_DB_FILE_MOCK)

    def test_request(self):
        query = Query('https://postman-echo.com/get', {'foo1': 'bar1', 'foo2': 'bar2', 'limit': 2})
        self.assertTrue(self.api.request(query))

    def test_can_create_cache(self):
        self.api = APICached()


if not os.path.exists('ACCESS_ID.txt'):
    from warnings import warn
    warn('TestVBBAPICached will not run, API key is missing')
else:
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
            # should be able to operate both on GPSPoint and Position objects
            position = Position(52.5219216,13.411026,'0','Alexanderplatz')
            result3 = self.api.get_closest_stop(position)
            self.assertEqual(result3, result)

        def test_can_init_old_cache(self):
            cache = SQLiteCache(TEST_DB_FILE)
            with open('ACCESS_ID.txt') as f:
                ACCESS_ID = f.read().strip()
            api2 = VBBAPICached(access_id=ACCESS_ID, cache=cache)
            result = api2.get_closest_stop(GPSPoint(52.5219216,13.411026))
            self.assertEqual('900100024', result.id)

        def test_get_all_trips(self):
            start = Position(52.5219216, 13.411026, 900100003, 'Alexanderplatz')  # Alexanderplatz
            end = Position(52.5201169, 13.3865786, 900100001, 'Friedrichstrasse')  # Friedrichstrasse
            result = self.api.get_all_trips(start, end)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, list)
            self.assertIsInstance(result[0], Trip)

        def test_get_all_trips_fixed_datetime(self):
            start = Position(52.5219216, 13.411026, 900100003, 'Alexanderplatz')  # Alexanderplatz
            end = Position(52.5201169, 13.3865786, 900100001, 'Friedrichstrasse')  # Friedrichstrasse
            time = datetime(2020,10,1,12,0,0)
            result = self.api.get_all_trips(start, end, datetime_=time)
            self.assertIsNotNone(result)
            self.assertIsInstance(result, list)


if __name__ == '__main__':
    unittest.main()
