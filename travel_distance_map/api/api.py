"""
API interface.
"""

class API:
    def request(query):
        raise NotImplementedError()

    def get_closest_stop(self, gps_point):
        raise NotImplementedError()

    def get_all_trips(self, gps_point_start, gps_point_end):
        raise NotImplementedError()
