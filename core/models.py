from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.core.urlresolvers import reverse
from datetime import datetime, timedelta
from django.utils.text import slugify
from django.utils.timezone import now
from localflavor.us.models import PhoneNumberField, USStateField, USZipCodeField
from recurrence.fields import RecurrenceField

from .fields import MoneypatchedRecurrenceField
from .utils import get_point

import pytz


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
    slug = models.SlugField(blank=True, null=True, max_length=255)
    phone = PhoneNumberField(blank=True)
    url = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    description = models.TextField(blank=True)
    keywords = models.CharField(blank=True, max_length=255)
    point = models.PointField(blank=True, null=True)
    objects = models.GeoManager()

    def save(self, *args, **kwargs):
        if not self.slug:
            candidate_slug = slugify(self.title)[0:255]
            if self.__class__.objects.filter(slug=candidate_slug).exists():
                candidate_slug_counter = 1
                while True:
                    if not self.__class__.objects.filter(slug="%s-%s" % (candidate_slug, candidate_slug_counter)).exists():
                        break
                    candidate_slug_counter += 1

            self.slug = candidate_slug
        if self.address and not self.point:
            self.point = Point(**get_point(', '.join([self.address, self.city, self.state, self.zipcode])))
        return super(Venue, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title


class Organization(models.Model):
    ORG_TYPE_CHOICES = (
            ('democratic', 'Democratic Party Organization'),
            ('governing-body', 'Governing Body'),
            ('progressive', 'Progressive Organization'),
            # ('advocacy', 'Advocacy Group'),
            # ('politician', 'Politician'),
            ('candidate', 'Political Candidate'),
        )
    title = models.CharField(max_length=255)
    url = models.URLField(blank=True)
    slug = models.SlugField(blank=True, null=True, max_length=255) 
    organization_type = models.CharField(max_length=255, choices=ORG_TYPE_CHOICES, null=True, blank=True)
    objects = models.GeoManager()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            candidate_slug = slugify(self.title)[0:255]
            if self.__class__.objects.filter(slug=candidate_slug).exists():
                candidate_slug_counter = 1
                while True:
                    if not self.__class__.objects.filter(slug="%s-%s" % (candidate_slug, candidate_slug_counter)).exists():
                        break
                    candidate_slug_counter += 1

            self.slug = candidate_slug
        return super(Organization, self).save(*args, **kwargs)


class EventQueryset(models.query.GeoQuerySet):

    def filter_by_date(self, as_occurrences=False, **kwargs):
        
        midnight_hawaii = datetime.combine(datetime.now(pytz.timezone('US/Hawaii')), datetime.min.time())
        future_date = midnight_hawaii + timedelta(**kwargs)
        queryset = self.all()
        events = filter(lambda e: len(e.recurrences.between(midnight_hawaii, future_date, inc=True)) > 0, queryset)
        if as_occurrences:
            occurrences = []
            for e in events:
                occurrences += e.recurrences.between(midnight_hawaii, future_date, inc=True)
            return occurrences
        else:
            return self.filter(pk__in=map(lambda e: e.pk, events))


class Event(models.Model):
    EVENT_TYPE_CHOICES = (
            ('party-event', 'Party Event'),
            ('governing-body-event', 'Governing Body Event'),
            ('volunteer', 'Volunteering Event'),
            ('advocacy', 'Advocacy'),
            ('rally', 'Rally'),
            ('forum', 'Forum'),
            ('community', 'Community Meetup'),
            (None, 'Uncategorized Event'),
        )
    title = models.CharField(max_length=255)
    venue = models.ForeignKey(Venue, null=True, blank=True)
    url = models.URLField(blank=True)
    slug = models.SlugField(blank=True, null=True, max_length=255)
    description = models.TextField(blank=True)
    start = models.TimeField(default=round_hours)
    end = models.TimeField(default=round_two_hours)
    recurrences = MoneypatchedRecurrenceField(null=True)
    event_type = models.CharField(max_length=255, choices=EVENT_TYPE_CHOICES, null=True, blank=True)
    host = models.ForeignKey(Organization, blank=True, null=True)
    objects = EventQueryset.as_manager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("event_detail", kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            candidate_slug = slugify(self.title)[0:255]
            if self.__class__.objects.filter(slug=candidate_slug).exists():
                candidate_slug_counter = 1
                while True:
                    if not self.__class__.objects.filter(slug="%s-%s" % (candidate_slug, candidate_slug_counter)).exists():
                        break
                    candidate_slug_counter += 1

            self.slug = candidate_slug
        return super(Event, self).save(*args, **kwargs)

    def dates(self, *args, **kwargs):
        if not kwargs:
            kwargs = {'days': 60}
        midnight_hawaii = datetime.combine(datetime.now(pytz.timezone('US/Hawaii')), datetime.min.time())
        future_date = midnight_hawaii + timedelta(**kwargs)
        return [i for i in self.recurrences.between(after=midnight_hawaii, before=future_date, inc=True)]