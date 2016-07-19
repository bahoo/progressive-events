import json
import urllib

from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Q
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import DetailView, TemplateView, View


from .forms import SearchForm, VenueForm, OrganizationForm, EventForm
from .models import Event, Venue
from .utils import get_point



class EventDetailView(DetailView):
    template_name = 'event_detail.html'
    model = Event



class MiniAPIView(View):
    search_field = 'title'
    api_fields = ['id', 'title']

    def get_searches(self, request):
        if request.GET.get('search'):
            return {'%s__icontains' % self.search_field: request.GET.get('search')}
        return {}

    def get(self, request, *args, **kwargs):
        return JsonResponse(list(self.model.objects.filter(**self.get_searches(request)).values(*self.api_fields)), safe=False)


class VenueAPIView(MiniAPIView):
    model = Venue
    api_fields = ['id', 'title', 'address', 'city', 'state', 'zipcode']


class MapView(TemplateView):
    template_name = 'map.html'

    def get_context_data(self, **kwargs):
        context = super(MapView, self).get_context_data(**kwargs)

        initial_data = {'address': 'Seattle, WA', 'distance': '15', 'days': '30',
                            'event_types': list(k for (k, v) in Event.EVENT_TYPE_CHOICES)}

        replacement_data = {}

        for k, v in initial_data.iteritems():
            if self.request.GET.get(k, None):
                if k == 'event_types':
                    replacement_data[k] = self.request.GET.getlist(k)
                else:
                    replacement_data[k] = self.request.GET.get(k)

        search_form = SearchForm(dict(initial_data, **replacement_data))

        point = GEOSGeometry('POINT(%(x)s %(y)s)' % get_point(search_form.data['address']), srid=4326)

        event_type_filter = Q()
        event_types = search_form.data.get('event_types', None)
        if event_types and len(event_types) != len(Event.EVENT_TYPE_CHOICES):
            for event_type in search_form.data['event_types']:
                event_type_filter = event_type_filter | Q(event_type=event_type)

        events = Event.objects.filter(event_type_filter).filter(venue__point__distance_lte=(point, D(mi=float(search_form.data['distance'])))).select_related('venue', 'host').filter_by_date(days=int(search_form.data['days'])).annotate(distance=Distance('venue__point', point)).order_by('distance')

        context['events'] = events
        context['now'] = datetime.now()
        context['future'] = datetime.now() + timedelta(days=int(search_form.data['days']))
        context['search_form'] = search_form
        context['point'] = point

        return context


class AddView(TemplateView):
    template_name = 'add.html'

    def post(self, *args, **kwargs):
        venue_form = VenueForm(self.request.POST or None, prefix='venue')
        event_form = EventForm(self.request.POST or None, prefix='event')
        organization_form = OrganizationForm(self.request.POST or None, prefix='organization')

        if (venue_form.data['venue-venue_id'] or venue_form.is_valid()) and \
                event_form.is_valid() and \
                organization_form.is_valid():
            organization = organization_form.save()
            if venue_form.data['venue-venue_id']:
                venue = Venue.objects.get(pk=int(venue_form.data['venue-venue_id']))
            else:
                venue = venue_form.save()
            event = event_form.save(commit=False)
            event.host = organization
            event.venue = venue
            event.save()

            messages.success(self.request, 'Your event was added. Thanks for submitting it!')

            return redirect('/?address=%s' %  urllib.quote(', '.join([venue.city, venue.state])))

        else:

            messages.error(self.request, 'There was an error in your event. Please check below for details.')

        return self.get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(AddView, self).get_context_data(**kwargs)

        # probably a more DIY friendly way to do this with multiple forms but
        venue_form = VenueForm(self.request.POST or None, prefix='venue')
        event_form = EventForm(self.request.POST or None, prefix='event')
        organization_form = OrganizationForm(self.request.POST or None, prefix='organization')
        context['venue_form'] = venue_form
        context['event_form'] = event_form
        context['organization_form'] = organization_form

        return context


class WhyView(TemplateView):
    template_name = 'why.html'