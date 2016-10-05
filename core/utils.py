import googlemaps
import json
import os
import redis
from django.conf import settings


def get_point(address):
    geolocator = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    try:
        r = redis.from_url(os.environ.get("REDIS_URL", "localhost:6379"))
        location = json.loads(r.get(address))
    except:
        # gracefully fails if redis is absent
        location = geolocator.geocode(address)[0]['geometry']['location']
        try:
            # cache it for 30 days.
            r.setex(address, json.dumps(location), 2592000)
        except:
            pass
    return {'x': location['lng'], 'y': location['lat']}

def get_venue(raw_venue):
    '''
    Returns a venue item from a raw venue. Contains the following information:
    {
        "title" : "Name of the place if any",
        "address" : "street address"
        "city" : "City of the area"
        "state": "State of the location"
        "zipcode": "Zipcode of place if any",
        "lat": "latitude of the venue",
        "lon": "longitude of the venue"
    }
    '''
    location = None
    geolocator = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    try:
        r = redis.from_url(os.environ.get("REDIS_URL", "localhost:6379"))
        location = json.loads(r.get(address))
    except:
        print raw_venue
        
        result = None
        try:
            result = geolocator.geocode(raw_venue)
        except:
            return None
        
        location = {}
        
        if len(result) == 0:
            return None
            
        for i in result[0]['address_components']:
            if 'street_number' in i['types']:
                location['street_number'] = i['short_name']
            if 'route' in i['types']:
                location['route'] = i['short_name']
            if 'subpremise' in i['types']:
                location['subpremise'] = i['short_name']
            if 'neighborhood' in i['types']:
                location['neighborhood'] = i['short_name']
            if 'locality' in i['types']:
                location['locality'] = i['short_name']
            if 'administrative_area_level_1' in i['types']:
                location['state'] = i['short_name']
            if 'postal_code' in i['types']:
                location['zipcode'] = i['short_name']
            
        if 'geometry' in result[0]:
            location['point'] = result[0]['geometry']['location']
            
        try:
            r.setex(raw_venue, json.dumps(location), 2592000)
        except:
            pass
            
    return location
