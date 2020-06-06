import math

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

    def distance_utf(self, other):
        def toRadians(deg):
            return deg * math.pi / 180.0

        R = 6371e3; # metres
        lat1, lon1 = self.lat, self.lon
        lat2, lon2 = other.lat, other.lon
        phi1 = toRadians(lat1)
        phi2 = toRadians(lat2)
        delta_phi = toRadians(lat2-lat1)
        delta_lambda = toRadians(lon2-lon1)

        a = math.sin(delta_phi/2) * math.sin(delta_phi/2) + \
                math.cos(phi1) * math.cos(phi2) * \
                math.sin(delta_lambda/2) * math.sin(delta_lambda/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        d = R * c
        return d


class Position:
    def __init__(self, lat, lon, identifier, name):
        self.point = GPSPoint(lat, lon)
        self.id = identifier
        self.name = name

    def __eq__(self, other):
        return self.id == other.id and self.name == other.name and self.point == other.point

    def __str__(self):
        return str({'id': self.id,
                'name': self.name,
                'point': str(self.point)})

    def __repr__(self):
        return self.__str__()
