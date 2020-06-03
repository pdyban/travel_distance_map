import unittest
from travel_distance_map import VBBAPICached, Query

@unittest.skip
class TestVBBAPICached(unittest.TestCase):
    def setUp(self):
        self.api = VBBAPICached()

    def test_request(self):
        query = Query('https://postman-echo.com/get', {'foo1': 'bar1', 'foo2': 'bar2'})
        self.assertEqual('''{
                  "args": {
                    "foo1": "bar1",
                    "foo2": "bar2"
                  },
                  "headers": {
                    "x-forwarded-proto": "https",
                    "host": "postman-echo.com",
                    "accept": "*/*",
                    "accept-encoding": "gzip, deflate",
                    "cache-control": "no-cache",
                    "postman-token": "5c27cd7d-6b16-4e5a-a0ef-191c9a3a275f",
                    "user-agent": "PostmanRuntime/7.6.1",
                    "x-forwarded-port": "443"
                  },
                  "url": "https://postman-echo.com/get?foo1=bar1&foo2=bar2"
                }''',
            api.request(query))


if __name__ == '__main__':
    unittest.main()
