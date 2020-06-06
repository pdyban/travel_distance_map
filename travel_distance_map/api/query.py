"""
Query objects that stores lists of parameters and generates URL queries on demand.
"""
import json

class Query(dict):
    def __init__(self, rootUrl, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self['rootUrl'] = rootUrl

    def __str__(self):
        if not self.keys:
            return rootUrl
        return '{}?'.format(self['rootUrl']) + '&'.join('{}={}'.format(key, value) for (key, value) in self.items())

    def to_json(self):
        return json.dumps(self)
