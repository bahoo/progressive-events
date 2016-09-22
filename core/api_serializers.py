from rest_framework import serializers
from .models import Event, Organization, Venue


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        exclude = []


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
    dates = serializers.SerializerMethodField()
    recurrence_rules = serializers.SerializerMethodField()

    def get_recurrence_rules(self, obj):
        return [rule.to_text().title() for rule in obj.recurrences.rrules ]

    def get_dates(self, obj):
        return [d.date() for d in obj.dates(days=int(self.context['request'].GET.get('days', 60)))]


    class Meta:
        model = Event
        exclude = ['recurrences', 'id']