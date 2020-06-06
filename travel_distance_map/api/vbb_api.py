"""
VBB API implementation.
"""

from .api import API
from .query import Query
from ..cache import SQLiteCache
from ..primitives import APIError, Position
import requests
import json
from datetime import datetime, timedelta

class VBBAPI(API):
    def __init__(self, access_id):
        API.__init__(self)
        self.ACCESS_ID = access_id
        self.base_url = "https://demo.hafas.de/openapi/vbb-proxy/"

    def request(self, query):
        response = requests.get(query)
        js = json.loads(response.text)
        if 'errorCode' in js and js['errorCode'] == 'API_QUOTA':
            raise APIError(js['errorText'])
        return js

    def get_closest_stop(self, point):
        if isinstance(point, Position):
            point = point.point  # extract GPSPoint from Position
        endpoint = self.base_url + 'location.nearbystops'
        parameters = {}
        parameters['accessId'] = self.ACCESS_ID
        parameters['format'] = 'json'
        parameters['originCoordLong'] = point.lon
        parameters['originCoordLat'] = point.lat
        parameters['maxNo'] = 1
        parameters['r'] = 2000
        query = Query(endpoint, parameters)
        response = self.request(query)

        for key, result in response.items():
            if 'TechnicalMessage' in result:
                break

            for location in result:
                try:
                    loc = location['StopLocation']
                    return Position(loc['lat'], loc['lon'], loc['extId'], loc['name'])
                except TypeError as e:
                    continue

        return None

    def get_all_trips(self, position_start, position_end, datetime_=None):
        origin_extid, dest_extid = position_start.id, position_end.id
        endpoint = self.base_url + 'trip'
        parameters = {}
        parameters['accessId'] = self.ACCESS_ID
        parameters['format'] = 'json'
        parameters['originExtId'] = position_start.id
        parameters['destExtId'] = position_end.id
        parameters['totalWalk'] = '1,0,5000'
        parameters['originWalk'] = '1,0,5000'
        parameters['destWalk'] = '1,0,5000'
        parameters['totalBike'] = '1,0,5000'
        parameters['originBike'] = '1,0,5000'
        parameters['destBike'] = '1,0,5000'
        if datetime_ is not None:
            date_ = datetime_.strftime('%Y-%m-%d')
            time_ = datetime_.strftime('%H:%M:%S')
            duration = 20  # mins
            parameters['date'] = date_
            parameters['time'] = time_
            parameters['duration'] = duration
        query = Query(endpoint, parameters)

        try:
            response = self.request(query)
        except APIError as e:
            response = {}

        return self.extract_trips_from_response(response)

    ### auxilliary functions

    def extract_trips_from_response(self, response):
        trips = []
        try:
            if 'errorCode' in response and response['errorCode'] == 'SVC_NO_RESULT':
                # print('Could not find a trip')
                pass
            elif 'errorCode' in response and response['errorCode'] == 'SVC_LOC_EQUAL': # start and dest are equal -> 0 time
                trips.append((timedelta(seconds=0.0), ()),)

            for trip in response.get('Trip', []):
                leglist = trip['LegList']

                for key in leglist:
                    travel_time = timedelta()
                    legs = []
                    for leg in leglist['Leg']:
                        # print(leg, len(leg))
                        leg_origin, leg_dest = leg['Origin'], leg['Destination']
                        if leg_origin['name'] not in legs:
                            legs.append(leg_origin['name'])
                        # print(leg_origin['time'], leg_dest['time'])
                        leg_origin_time = datetime.strptime(leg_origin['time'], '%H:%M:%S')
                        leg_dest_time = datetime.strptime(leg_dest['time'], '%H:%M:%S')
                        td = timedelta() + leg_dest_time - leg_origin_time
                        travel_time += td
                        legs.append(leg_dest['name'])
                    # print('TOTAL TRAVEL TIME: {}'.format(travel_time))
                    trips.append((travel_time, legs))
        except KeyError as e:
            print('Error:', e)

        return trips

    def append_access_id(self, endpoint):
        return endpoint + ('?','&')[endpoint.find('?') > -1] + "accessId={ACCESS_ID}".format(ACCESS_ID=self.ACCESS_ID)

    def force_json_format(self, endpoint):
        return endpoint + ('?','&')[endpoint.find('?') > -1] + "format=json"

    def set_latlon(self, endpoint, point, mode):
        return endpoint + ('?','&')[endpoint.find('?') > -1] + \
                "{mode}CoordLat={point[0]}".format(mode=mode, point=point) + '&' + \
                "{mode}CoordLon={point[1]}".format(mode=mode, point=point)

    def set_origin_latlon(self, endpoint, point):
        return set_latlon(endpoint, point, 'origin')

    def set_dest_latlon(self, endpoint, point):
        return set_latlon(endpoint, point, 'dest')

    def set_extid(self, endpoint, extid, mode):
        return endpoint + ('?','&')[endpoint.find('?') > -1] + "{}ExtId={}".format(mode,extid)

    def set_origin_extid(self, endpoint, extid):
        return set_extid(endpoint, extid, 'origin')

    def set_dest_extid(self, endpoint, extid):
        return set_extid(endpoint, extid, 'dest')

    def append_date_and_time(self, endpoint, datetime_):
        date_ = datetime_.strftime('%Y-%m-%d')
        time_ = datetime_.strftime('%H:%M:%S')
        duration = 20  # mins
        return endpoint + ('?','&')[endpoint.find('?') > -1] + "date={}&time={}&duration={}".format(date_, time_, duration)

    def enable_walk_routes(self, endpoint):
        return enable_alt_routes(endpoint, 'Walk')

    def enable_bike_routes(self, endpoint):
        return enable_alt_routes(endpoint, 'Bike')

    def enable_alt_routes(self, endpoint, mode):
        return endpoint + ('?','&')[endpoint.find('?') > -1] + "total{0}=1,0,5000&origin{0}=1,0,5000&dest{0}=1,0,5000".format(mode)


class VBBAPICached(VBBAPI):
    def __init__(self, access_id, cache=None):
        VBBAPI.__init__(self, access_id)
        if cache is not None:
            self.cache = cache
        else:
            self.cache = SQLiteCache('cache.sqlite')

    def request(self, query):
        if query in self.cache:
            js = self.cache[query]
            # print(js)
            return json.loads(js)

        response = VBBAPI.request(self, query)
        self.cache[query] = json.dumps(response)
        return response
