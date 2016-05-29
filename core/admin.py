from django.contrib.gis import admin
from django.contrib.gis.geos import Point
from django.conf import settings
from .models import Venue, Event, Organization
import googlemaps


@admin.register(Venue)
class VenueAdmin(admin.OSMGeoAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ['title', 'address', 'city', 'state']
    list_filter = ['state']

    def save_model(self, request, obj, form, change):
        if not obj.point:
            obj.point = Point(0,0)
            address = ', '.join([obj.address, obj.city, obj.state, obj.zipcode])
            geolocator = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
            geocoded_address = geolocator.geocode(address)
            location = geocoded_address[0]['geometry']['location']
            obj.point.x, obj.point.y = location['lng'], location['lat']
        obj.save()


@admin.register(Organization)
class OrganizationAdmin(admin.OSMGeoAdmin):
    list_display = ['title', 'organization_type']
    list_filter = ['organization_type']


@admin.register(Event)
class EventAdmin(admin.OSMGeoAdmin):
    list_display = ['title', 'event_type']
    list_filter = ['event_type']