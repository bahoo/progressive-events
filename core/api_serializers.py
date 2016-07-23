from rest_framework import serializers
from .models import Event, Organization, Venue


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        exclude = ['id']


class VenueSerializer(serializers.ModelSerializer):
    point = serializers.SerializerMethodField()


    def get_point(self, obj):
        return {'x': obj.point.x, 'y': obj.point.y}

    class Meta:
        model = Venue
        exclude = []


class EventSerializer(serializers.ModelSerializer):
    host = OrganizationSerializer()
    venue = VenueSerializer()


    class Meta:
        model = Event
        exclude = ['recurrences', 'id']