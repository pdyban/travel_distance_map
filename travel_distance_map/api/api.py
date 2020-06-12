"""
API interface.
"""
import requests
import json

class API:
    def request(self, query):
        response = requests.get(query)
        js = json.loads(response.text)
        if 'errorCode' in js and js['errorCode'] == 'API_QUOTA':
            raise APIError(js['errorText'])
        return js


class APICached(API):
    def __init__(self, cache=None):
        API.__init__(self)
        if cache is not None:
            self.cache = cache
        else:
            self.cache = SQLiteCache('cache.sqlite')

    def request(self, query):
        if query in self.cache:
            js = self.cache[query]
            return json.loads(js)

        response = API.request(self, query)
        self.cache[query] = json.dumps(response)
        return response
