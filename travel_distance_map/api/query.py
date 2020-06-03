"""
Query objects that stores lists of parameters and generates URL queries on demand.
"""

class Query(dict):
    def __init__(self, rootUrl, *args, **kwargs):
        self.rootUrl = rootUrl
        dict.__init__(self, *args, **kwargs)

    def __str__(self):
        if not self.keys:
            return rootUrl
        return '{}?'.format(self.rootUrl) + '&'.join('{}={}'.format(key, value) for (key, value) in self.items())
