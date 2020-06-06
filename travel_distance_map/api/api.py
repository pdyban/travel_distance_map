"""
API interface.
"""

class API:
    def request(query):
        raise NotImplementedError()

    def get_closest_stop(self, gps_point):
        raise NotImplementedError()

    def get_all_trips(self, position_start, position_end):
        raise NotImplementedError()
