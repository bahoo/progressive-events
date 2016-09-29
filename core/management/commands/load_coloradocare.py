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

class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)
                    
    def handle(self, *args, **options):
    # now do the things that you want with your models here
        filename = options['filename'][0]
        print "%s -- filename" % filename
        
        org = self.store_organization()
        with open(filename, 'rb') as data_file:
            data = json.loads(data_file.read())
            counter = 1
            
            # VCalendar has its own set of event list
            for item in data['VCALENDAR'][0]['VEVENT']:
                #Skip recurrences
                if 'RRULE' in item: 
                    next
                    
                address = item['LOCATION'].split('\\,') 
                if len(address) <= 1: 
                    next
                else:
                    # Get Venue
                    (title, add, city, state, zipcode) = self.extract_address(address)
                    venue = self.store_venue(title, add, city, state, zipcode)
                    
                    #Parse datetime
                    e_start = self.parse_datetime(item)
                    
                    self.store_event(venue, org, item['SUMMARY'], '', item['DESCRIPTION'], e_start)

            # Root object also has its own set of event list
            for item in data['VEVENT']:
                if 'RRULE' in item: 
                    next
                    
                address = item['LOCATION'].split('\\,')
                
                if len(address) <= 1: 
                    next
                else:
                    (title, add, city, state, zipcode) = self.extract_address(address)
                    venue = self.store_venue (title, add, city, state, zipcode)
                    
                    e_start = self.parse_datetime(item)
                    
                    self.store_event(venue, org, item['SUMMARY'], '', item['DESCRIPTION'], e_start)
            
    def extract_address(self, address):
        title = None
        complete_address = None
        city = None

        address_array = [i.encode("utf-8").strip() for i in address]
        state_zip = address_array.pop()
        m = re.match('(\w{2})\s+(\d{5})', state_zip)
        
        if m == None:
            print(address)
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
    
    def parse_datetime(self, item):
        e_start = None
        
        if 'DTSTART;TZID=America/Los_Angeles' in item:
            dt = parser.parse(item['DTSTART;TZID=America/Los_Angeles']).replace(tzinfo=pytz.timezone("America/Los_Angeles"))
            e_start = dt.astimezone(pytz.timezone("America/Denver")).replace(minute=dt.minute)
        elif 'DTSTART;TZID=America/Denver' in item:
            e_start = parser.parse(item['DTSTART;TZID=America/Denver'])
        elif 'DTSTART' in item:
            dt = parser.parse(item['DTSTART']).replace(tzinfo=pytz.timezone("UTC"))
            e_start = dt.astimezone(pytz.timezone("America/Denver"))
        elif 'DTSTART;VALUE=DATE' in item:
            dt = parser.parse(item['DTSTART;VALUE=DATE']).replace(tzinfo=pytz.timezone("UTC"))
            e_start = dt.astimezone(pytz.timezone("America/Denver"))
        else:
            return None
            
        return e_start    
        
    def store_event(self,venue, org, name, url, description, event_date):
        title=name
        url=''
        start=event_date.time()
        event_type='volunteer'
        recurrences=recurrence.Recurrence(
            rdates=[event_date]
        )
        
        result = Event.objects.filter(title=title).filter(start=start)
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
            print "[ORGANIZATION] Saving: ", organization.title
            return organization
        else:
            return result[0]
            
    def store_venue(self, title, address, city, state, zipcode):
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
                zipcode=zipcode
            )
            venue.save()
            print "[VENUE] Saving: ", venue.title
            return venue
        else:
            return result[0]
