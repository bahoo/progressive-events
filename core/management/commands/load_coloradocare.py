from django.core.management.base import BaseCommand
from core.models import Venue,Organization,Event
from pprint import pprint
from dateutil.tz import tzoffset
import pytz
import recurrence
import json
import datetime
import urllib
import time
import pprint
import re
from django.contrib.gis.geos import Point
from dateutil import parser
import requests
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry

from core.utils import get_venue

class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='*', default=False, type=str)
                    
    def handle(self, *args, **options):
        '''
        handle: If `filename` is specified, this reads through a file set by the user OR
                this takes in data from the ColoradoCare calendar automatically.
        '''
        filename = options['filename'][0] if options['filename'] else None
        
        # Load Data
        org = self.store_organization()
        data = None
        if filename:
            with open(filename, 'rb') as data_file:
                data = json.loads(data_file.read())
        else:
            request = requests.get(settings.COLORADO_CARE_URL)
            data = request.json()
        
        for item in data['items']:
            
            #PARSING
            url = item['htmlLink']
            title = item['summary'] if 'summary' in item else ''
            description = item['description'] if 'description' in item else ''
            location = item['location'] if 'location' in item else None
                
            # start date
            start_tz = None
            start_dt = None
            if 'start' in item:
                if 'dateTime' in item['start']:
                    start_dt = item['start']['dateTime']
                elif 'date' in item['start']:
                    start_dt = item['start']['date']
                
                if 'timeZone' in item['start']:
                    start_tz = item['start']['timeZone']
            
            # end date
            end_tz = None
            end_dt = None
            if 'end' in item:
                if 'dateTime' in item['end']:
                    end_dt = item['end']['dateTime']
                elif 'date' in item['end']:
                    end_dt = item['end']['date']
                
                if 'timeZone' in item['end']:
                    end_tz = item['end']['timeZone']
            
            
            # Extract VENUE
            venue = None
            if location is None or start_dt is None:
                next
            else:
                venue = self.parse_venue(location)
                
            if venue is None: 
                next
                
            # Extract datetime
            if start_dt is None:
                next
            else:
                e_start = self.parse_datetime(start_dt, start_tz)
                
            if end_dt is not None:
                e_end = self.parse_datetime(end_dt, end_tz)
            
            self.store_event(venue, org, title, description, url, e_start, e_start, e_end)
                
    def parse_venue(self, raw_venue):
        geocoded = get_venue(raw_venue)
        
        if geocoded is None:
            return None
            
        point = 'POINT (%f %f)' % (geocoded['point']['lat'], geocoded['point']['lng'])
        address = '%s %s' % (geocoded['street_number'] if 'street_number' in geocoded else '', geocoded['route'] if 'route' in geocoded else '')
        city = None
        if 'locality' in geocoded:
            city = geocoded['locality']
        elif 'neighborhood' in geocoded:
            city = geocoded['neighborhood']
        else:
            city = None
        
        state = geocoded['state']
        zipcode = geocoded['zipcode'] if 'zipcode' in geocoded else ''
        
        venue = self.store_venue(raw_venue, address, city, state, zipcode, point = GEOSGeometry(point))
        return venue
                
    def extract_address(self, address):
        title = None
        complete_address = None
        city = None

        address_array = [i.encode("utf-8").strip() for i in address]
        state_zip = address_array.pop()
        m = re.match('(\w{2})\s+(\d{5})', state_zip)
        
        if m == None:
            zipcode = None
            state = None

        else:
            zipcode = m.group(2)
            state = m.group(1)
        
        if len(address_array) > 0:
            city = address_array.pop()
        if len(address_array) > 0:
            complete_address = address_array.pop()
        if len(address_array) > 0:
            title = address_array.pop()
        
        return (title, complete_address, city, state, zipcode)
    
    def parse_datetime(self, date_time, time_zone):
        '''
        Grab the date time aspect of the event line, and parse out the time and timezone
        Afterwhich, convert it to Denver time
        '''
        co_time = None
        
        dt = parser.parse(date_time).replace(tzinfo=pytz.timezone(time_zone)) if time_zone is not None else parser.parse(date_time)
        co_time = dt.astimezone(pytz.timezone("America/Denver")).replace(minute=dt.minute) if time_zone is not None else dt

        return co_time
        
    def store_event(self,venue, org, name, description, url, event_date, start, end):
        title=name
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
                end=end,
                start=start,
                recurrences=recurrences,
                event_type=event_type,
                host=org,
                venue=venue
            )
            new_event.save()
            return new_event
        else:
            return result[0]
                
    def store_organization(self):
        url = "http://www.coloradocare.org"
        organization_type='progressive'
        title = "ColoradoCare"
        
        result = Organization.objects.filter(url=url)
        if len(result) == 0:
            organization = Organization(
                title=title, 
                url=url,
                slug=url,
                organization_type=organization_type
            )
            organization.save()
            return organization
        else:
            return result[0]
            
    def store_venue(self, title, address, city, state, zipcode, point = None):
        venue = None
        point = None
                
        result = Venue.objects.filter(
                    title=title if title != None else '', 
                    city=city, 
                    address=address, 
                    state=state
                 )
        if len(result) == 0:
            venue = Venue(title=title if title != None else '', 
                city=city, 
                address=address, 
                state=state,
                zipcode=zipcode,
                point=point
            )
            venue.save()
            return venue
        else:
            return result[0]
