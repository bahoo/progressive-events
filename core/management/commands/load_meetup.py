from django.core.management.base import BaseCommand
from core.models import Venue,Organization,Event
from pprint import pprint
from dateutil.tz import tzoffset
import recurrence
import json
import datetime
import urllib
import time
from django.contrib.gis.geos import Point

class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)
                    
    def handle(self, *args, **options):
    # now do the things that you want with your models here
        filename = options['filename'][0]
        print "%s -- filename" % filename
        with open(filename, 'rb') as url_file:
            lines = [line.rstrip('\n') for line in url_file]
            for line in lines:
                # each line is a url group
                url = "https://api.meetup.com/2/events?offset=0&format=json&limited_events=False&group_urlname=" + line + "&photo-host=public&page=50&fields=&order=time&desc=false&status=upcoming"
                
                print "[URL] Reading: " + url
                response = urllib.urlopen(url)
                data = json.loads(response.read())
                for event in data['results']:
                    # Adding venue attributes
                    if 'venue' in event:
                        venue = self.store_venue(event['venue'])
                        organization = self.store_organization(event['group'])
                        self.store_event(event, venue, organization)
                    
                time.sleep(10)
                
    def store_event(self, event, venue, org):
        title=event['name']
        url=event['event_url']
        description=event['description'] if 'description' in event else ''
        event_date=datetime.datetime.fromtimestamp(event['time']/1000, tzoffset(None, event['utc_offset']/1000))
        start=event_date.time()
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
            return result[0]
                
    def store_organization(self, org):
        url = "http://www.meetup.com/" + org['urlname']
        organization_type='progressive'
        title = org['name']
        
        result = Organization.objects.filter(url=url)
        if len(result) == 0:
            organization = Organization(
                title=title, 
                url=url,
                slug=org['urlname'],
                organization_type=organization_type
            )
            organization.save()
            print "[ORGANIZATION] Saving: ", organization.title
            return organization
        else:
            return result[0]
            
    def store_venue(self, venue):
        title=venue['name']
        city=venue['city']
        address=venue['address_1']
        state=venue['state'] if 'state' in venue else ''
        zipcode=venue['zipcode'] if 'zipcode' in venue else ''
        point = None
        

        if 'lon' in venue and 'lat' in venue:
            point=Point(venue['lon'],venue['lat'])
        
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
