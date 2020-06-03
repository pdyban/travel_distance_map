
class APIError(RuntimeError):
    pass


class GPSPoint:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon


class Position(GPSPoint):
    def __init__(self, lat, lon, identifier, name):
        GPSPoint.__init__(self)
        self.id = identifier
        self.name = name
