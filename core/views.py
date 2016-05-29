from django.contrib.gis.measure import D
from django.contrib.gis.geos import GEOSGeometry
from django.shortcuts import render
from .models import Event, Venue
from datetime import datetime, timedelta


def test(request):
    pnt = GEOSGeometry('POINT(-122.283130 47.770473)', srid=4326)
    events = Event.objects.filter(venue__point__distance_lte=(pnt, D(mi=5))).select_related('venue', 'host').filter_by_date(days=45)
    return render(request, 'test.html', {'events': events, 'now': datetime.now(), 'future': datetime.now() + timedelta(days=45) })