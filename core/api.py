from django.conf.urls import url
from rest_framework import filters, generics

from .models import Event, Organization, Venue
from .api_serializers import EventSerializer, OrganizationSerializer, VenueSerializer


class EventFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        days = request.GET.get('days', None)

        if days:
            queryset = 




class EventList(generics.ListAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = (filters.DjangoFilterBackend, EventFilter)
    filter_fields = ['host__slug', 'event_type']


class OrganizationList(generics.ListAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    filter_backends = (filters.DjangoFilterBackend,)


class VenueList(generics.ListAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    filter_backends = (filters.DjangoFilterBackend,)
