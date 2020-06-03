import unittest
from travel_distance_map import VBBAPICached, Query


@unittest.skip
class TestVBBAPICached(unittest.TestCase):
    def setUp(self):
        self.api = VBBAPICached(access_id='')

    def test_request(self):
        # query = Query('https://postman-echo.com/get', {'foo1': 'bar1', 'foo2': 'bar2'})
        query = Query('https://postman-echo.com/get', {'foo1': 'bar1'})
        self.assertEqual("""{'args': {'foo1': 'bar1'}, 'headers': {'x-forwarded-proto': 'https', 'x-forwarded-port': '443', 'host': 'postman-echo.com', 'x-amzn-trace-id': 'Root=1-5ed7c472-0e46ca5391f8067d4e81a2e9', 'user-agent': 'python-requests/2.22.0', 'accept-encoding': 'gzip, deflate', 'accept': '*/*'}, 'url': 'https://postman-echo.com/get?foo1=bar1'}""",
            self.api.request(query))


if __name__ == '__main__':
    unittest.main()
