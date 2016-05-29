import googlemaps

from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.contrib.gis.geos import GEOSGeometry
from django.shortcuts import render

from .forms import SearchForm
from .models import Event, Venue


def search(request):

    initial_data = {'address': 'Seattle, WA', 'distance': '15', 'days': '45'}

    search_form = SearchForm(request.GET or initial_data)

    address = search_form.data.get('address', 'Seattle, WA')
    distance = int(search_form.data.get('distance', '15'))
    days = int(search_form.data.get('days', '45'))

    geolocator = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
    location = geolocator.geocode(address)[0]['geometry']['location']
    point = GEOSGeometry('POINT(%(lng)s %(lat)s)' % {'lng': location['lng'], 'lat': location['lat']}, srid=4326)

    events = Event.objects.filter(venue__point__distance_lte=(point, D(mi=distance))).select_related('venue', 'host').filter_by_date(days=days).annotate(distance=Distance('venue__point', point)).order_by('distance')
    return render(request, 'search.html',
                                            {'events': events,
                                            'now': datetime.now(),
                                            'future': datetime.now() + timedelta(days=days),
                                            'search_form': search_form,
                                            'point': point })