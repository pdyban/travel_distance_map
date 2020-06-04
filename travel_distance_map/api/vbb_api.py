"""
VBB API implementation.
"""

from .api import API
from .query import Query
from ..cache import SQLiteCache
import requests
import json

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
        parameters = {}
        endpoint = self.base_url + 'location.nearbystops'

        parameters['accessId'] = self.ACCESS_ID
        parameters['format'] = 'json'
        parameters['originCoordLong'] = point.lon
        parameters['originCoordLat'] = point.lat
        parameters['maxNo'] = 1
        parameters['r'] = 2000
        query = Query(self.base_url + 'location.nearbystops', parameters)
        response = self.request(query)

        for key, result in response.items():
            if 'TechnicalMessage' in result:
                break

            for location in result:
                try:
                    return location['StopLocation']
                except TypeError as e:
                    continue

        return None

    def get_all_trips(self, gps_point_start, gps_point_end, datetime_=None):
        origin_extid, dest_extid = gps_point_start.identifier, gps_point_end.identifier
        endpoint = self.base_url + 'trip'
        endpoint = self.append_access_id(endpoint)
        endpoint = self.force_json_format(endpoint)
        endpoint = self.set_origin_extid(endpoint, origin_extid)
        endpoint = self.set_dest_extid(endpoint, dest_extid)
        endpoint = self.enable_walk_routes(endpoint)
        endpoint = self.enable_bike_routes(endpoint)
        if datetime_ is not None:
            endpoint = self.append_date_and_time(endpoint, datetime_)

        try:
            response = self.request(endpoint)
        except APIError as e:
            response = {}

        return self.extract_trips_from_response(response)

    ### auxilliary functions

    def extract_trips_from_response(self, response):
        trips = []
        try:
            if response['errorCode'] == 'SVC_NO_RESULT':
                # print('Could not find a trip')
                pass
            elif response['errorCode'] == 'SVC_LOC_EQUAL': # start and dest are equal -> 0 time
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
            return self.cache[query]

        response = VBBAPI.request(self, query)
        self.cache[query] = response
        return response
