from rest_framework import serializers
from .models import Event, Organization, Venue


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        exclude = []


class VenueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Venue
        exclude = []


class EventSerializer(serializers.ModelSerializer):


    class Meta:
        model = Event
        exclude = []