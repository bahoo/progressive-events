import googlemaps
import json
import os
import redis
from django.contrib.gis.geos import GEOSGeometry
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
    point = GEOSGeometry('POINT(%(lng)s %(lat)s)' % {'lng': location['lng'], 'lat': location['lat']}, srid=4326)

    return point