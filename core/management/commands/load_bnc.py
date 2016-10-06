from django.core.management.base import BaseCommand
from core.models import Venue,Organization,Event
from pprint import pprint
from dateutil.tz import tzoffset
from dateutil.parser import parse
import recurrence
import json
from datetime import timedelta, datetime
import urllib2
import time
from django.contrib.gis.geos import Point
import os

# Focused on adding BNC data only
class Command(BaseCommand):
                    
    def handle(self, *args, **options):
    # now do the things that you want with your models here
        date_start= datetime.now().strftime("%Y-%m-%d")
        date_end = (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d")
        token = os.environ.get('BNC_TOKEN', None)
        url = "https://brandnewcongress.nationbuilder.com/api/v1/sites/brandnewcongress/pages/events?access_token={}&limit=3000&starting={}&ending={}"\
                .format(token, date_start, date_end)
        
        print "[URL] Reading: " + url
        request = urllib2.Request(url)
        request.add_header('Content-Type', 'application/json')
        request.add_header('Accept', 'application/json')
        pprint(request)
        response = urllib2.urlopen(request)
        
        data = json.loads(response.read())
        for event in data['results']:
            # Adding venue attributes
            print "Reading... ", event['title']
            
            # TEst event...
            if event['slug'] == 'event':
                continue
                
            if 'venue' in event:
                venue = self.store_venue(event['venue'])
                if venue != None:
                    organization = self.store_organization()
                    self.store_event(event, venue, organization)
            
        time.sleep(5)
                
    def store_event(self, event, venue, org):
        title=event['name']
        url=event['path']
        description=event['intro'] if 'intro' in event else ''
        event_date=parse(event['start_time'])
        start=event_date.time()
        end=parse(event['end_time']).time()
        event_type='volunteer'
        recurrences=recurrence.Recurrence(
            rdates=[event_date]
        )
        
        result = Event.objects.filter(url=url)
        if len(result) == 0:
            new_event = Event(
                title=title, 
                url=url,
                description=description,
                start=event_date,
                recurrences=recurrences,
                event_type=event_type,
                host=org,
                venue=venue
            )
            new_event.save()
            print "[EVENT] Saving: " + new_event.title
            return new_event
        else:
            update_event = result[0]
            update_event.title = title
            update_event.url = url
            update_event.description = description
            update_event.start = event_date
            update_event.recurrences=recurrences
            update_event.event_type=event_type
            update_event.host=org
            update_event.venue=venue
            update_event.save()
            return update_event
                
    def store_organization(self):
        url = 'http://www.brandnewcongress.org'
        organization_type='progressive'
        title = 'Brand New Congress'
        
        result = Organization.objects.filter(url=url)
        if len(result) == 0:
            organization = Organization(
                title=title, 
                url=url,
                organization_type=organization_type
            )
            organization.save()
            print "[ORGANIZATION] Saving: ", organization.title
            return organization
        else:
            return result[0]
            
    def store_venue(self, venue):
        title=venue['name']
        if 'address' not in venue or venue['address'] == None:
            return None
        
        city=venue['address']['city'] if 'city' in venue['address'] else ''
        address=venue['address']['address_1'] if 'address_1' in venue['address'] else ''
        state=venue['address']['state'] if 'state' in venue['address'] else ''
        zipcode=venue['address']['zip'] if 'zip' in venue['address'] else ''
        point = None
        

        if 'lon' in venue and 'lat' in venue['address']:
            point=Point(venue['address']['lng'],venue['address']['lat'])
        
        result = Venue.objects.filter(
                    title=title, 
                    city=city, 
                    address=address, 
                    state=state
                 )
        if len(result) == 0:
            venue = Venue(title=title, 
                city=city, 
                address=address, 
                state=state,
                zipcode=zipcode,
                point=point
            )
            venue.save()
            print "[VENUE] Saving: ", venue.title
            return venue
        else:
            return result[0]
