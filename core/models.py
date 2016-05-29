from __future__ import unicode_literals

from django.contrib.gis.db import models
from datetime import datetime, timedelta
from django.utils.timezone import now
from localflavor.us.models import PhoneNumberField, USStateField, USZipCodeField
from recurrence.fields import RecurrenceField


def round_hours(hours=1):
    return now().replace(minute=0).replace(second=0) + timedelta(hours=hours)

def round_two_hours():
    return round_hours(2)

class Venue(models.Model):
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = USStateField()
    zipcode = USZipCodeField(blank=True)
    slug = models.SlugField()
    phone = PhoneNumberField(blank=True)
    url = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    description = models.TextField(blank=True)
    keywords = models.CharField(blank=True, max_length=255)
    point = models.PointField(blank=True, null=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.title


class Organization(models.Model):
    ORG_TYPE_CHOICES = (
            ('democratic', 'Democratic Party Organization'),
            ('governing-body', 'Governing Body'),
            ('progressive', 'Progressive Organization'),
            ('candidate', 'Political Candidate'),
        )
    title = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    organization_type = models.CharField(max_length=255, choices=ORG_TYPE_CHOICES, null=True, blank=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.title


class EventQueryset(models.query.GeoQuerySet):

    def filter_by_date(self, as_occurrences=False, assign_occurrences=True, **kwargs):
        future_date = datetime.now() + timedelta(**kwargs)
        queryset = self.all()
        events = filter(lambda e: len(e.recurrences.between(datetime.now(), future_date)) > 0, queryset)
        if as_occurrences:
            occurrences = []
            for e in events:
                occurrences += e.recurrences.between(datetime.now(), future_date)
            return occurrences
        else:
            if assign_occurrences:
                for e in events:
                    e.dates = e.recurrences.between(datetime.now(), future_date)
            return events


class Event(models.Model):
    EVENT_TYPE_CHOICES = (
            ('party-event', 'Party Event'),
            ('governing-body-event', 'Governing Body Event'),
            ('volunteer', 'Volunteering Event'),
        )
    title = models.CharField(max_length=255)
    venue = models.ForeignKey(Venue, null=True, blank=True)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    start = models.TimeField(default=round_hours)
    end = models.TimeField(default=round_two_hours)
    recurrences = RecurrenceField(null=True)
    event_type = models.CharField(max_length=255, choices=EVENT_TYPE_CHOICES, null=True, blank=True)
    host = models.ForeignKey(Organization, blank=True, null=True)
    objects = EventQueryset.as_manager()

    def __unicode__(self):
        return self.title