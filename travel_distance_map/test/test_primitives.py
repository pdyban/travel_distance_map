import unittest
from travel_distance_map import GPSPoint, Position


class TestGPSPoint(unittest.TestCase):
    def test_distance_utf(self):
        point1 = GPSPoint(52.5219216, 13.411026)  # Alexanderplatz
        point2 = GPSPoint(52.5201169, 13.3865786)  # Friedrichstrasse
        dist = point1.distance_utf(point2)
        self.assertEqual(dist, 1666.210510534654)

    def test_equals(self):
        point1 = GPSPoint(52.5219216, 13.411026)  # Alexanderplatz
        point2 = GPSPoint(52.5201169, 13.3865786)  # Friedrichstrasse
        self.assertTrue(point1 == point1)
        self.assertTrue(not point1 == point2)


class TestPosition(unittest.TestCase):
    def test_equals(self):
        pos1 = Position(52.5219216, 13.411026, 900100003, 'Alexanderplatz')
        pos2 = Position(52.5201169, 13.3865786, 900100001, 'Friedrichstrasse')
        self.assertTrue(pos1 == pos1)
        self.assertTrue(not pos1 == pos2)
