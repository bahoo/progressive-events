import django_filters

from django.conf.urls import url
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Q

from rest_framework import filters, generics

from .api_serializers import EventSerializer, OrganizationSerializer, VenueSerializer
from .forms import SearchForm
from .models import Event, Organization, Venue
from .utils import get_point


class EventFilterBackend(filters.BaseFilterBackend):

    def prepare_search_form(self, request):

        initial_data = {'address': 'Seattle, WA', 'distance': '15', 'days': '30', 'event_types': list(k for (k, v) in Event.EVENT_TYPE_CHOICES)}

        for k, v in initial_data.iteritems():
            if request.GET.get(k, None):
                if k == 'event_types':
                    initial_data[k] = request.GET.getlist(k)
                else:
                    initial_data[k] = request.GET.get(k)

        search_form = SearchForm(initial_data)

        return search_form

    def get_point(self, address):
        return GEOSGeometry('POINT(%(x)s %(y)s)' % get_point(address), srid=4326)

    def filter_queryset(self, request, queryset, view, search_form=None, point=None):

        if not search_form:
            search_form = self.prepare_search_form(request)

        if not point:
            point = self.get_point(search_form['address'])

        event_type_filter = Q()
        for event_type in search_form.data['event_types']:
            event_type_filter = event_type_filter | Q(event_type=event_type)

        return queryset.filter(event_type_filter) \
                        .filter(venue__point__distance_lte=(point, D(mi=float(search_form.data['distance'])))) \
                        .select_related('venue', 'host') \
                        .filter_by_date(days=int(search_form.data['days'])) \
                        .annotate(distance=Distance('venue__point', point)) \
                        .order_by('distance')


class EventFilter(filters.FilterSet):
    org = django_filters.CharFilter(name='host__slug')
    event = django_filters.CharFilter(name='slug')

    class Meta:
        model = Event
        fields = ['event', 'org']


class EventList(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = (filters.DjangoFilterBackend, EventFilterBackend)
    filter_class = EventFilter
    filter_fields = ['event', 'event_type', 'org']


class OrganizationList(generics.ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    filter_backends = (filters.DjangoFilterBackend,)


class VenueFilter(filters.FilterSet):
    search = django_filters.CharFilter(name='title', lookup_expr='icontains')

    class Meta:
        model = Venue
        fields = ['search']


class VenueList(generics.ListAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = VenueFilter
    filter_fields = ['search']
