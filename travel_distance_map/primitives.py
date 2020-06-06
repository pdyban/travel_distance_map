
class APIError(RuntimeError):
    pass


class GPSPoint:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def __eq__(self, other):
        return self.lat == other.lat and self.lon == other.lon

    def __str__(self):
        return '({},{})'.format(self.lat, self.lon)


class Position(GPSPoint):
    def __init__(self, lat, lon, identifier, name):
        GPSPoint.__init__(self, lat, lon)
        self.id = identifier
        self.name = name

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name and GPSPoint.__eq__(self, other)

    def __str__(self):
        return str({'id': self.id,
                'name': self.name,
                'point': GPSPoint.__str__(self)})

    def __repr__(self):
        return self.__str__()
