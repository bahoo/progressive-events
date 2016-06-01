from datetime import datetime, timedelta
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.generic import TemplateView


from .forms import SearchForm, VenueForm, OrganizationForm, EventForm
from .models import Event, Venue
from .utils import get_point


class MapView(TemplateView):
    template_name = 'map.html'

    def get_context_data(self, **kwargs):
        context = super(MapView, self).get_context_data(**kwargs)

        initial_data = {'address': 'Seattle, WA', 'distance': '15', 'days': '30', 'event_types': list(k for (k, v) in Event.EVENT_TYPE_CHOICES)}
        search_form = SearchForm(self.request.GET or initial_data)
        address = search_form.data.get('address', initial_data.get('address'))
        distance = int(search_form.data.get('distance', initial_data.get('distance')))
        days = int(search_form.data.get('days', initial_data.get('days')))

        point = GEOSGeometry('POINT(%(x)s %(y)s)' % get_point(address), srid=4326)

        type_filter = Q()
        event_types = self.request.GET.getlist('event_types', initial_data.get('event_types', []))
        if event_types:
            for event_type in event_types:
                type_filter = type_filter | Q(event_type=event_type)

        events = Event.objects.filter(type_filter).filter(venue__point__distance_lte=(point, D(mi=distance))).select_related('venue', 'host').filter_by_date(days=days).annotate(distance=Distance('venue__point', point)).order_by('distance')

        context['events'] = events
        context['now'] = datetime.now()
        context['future'] = datetime.now() + timedelta(days=days)
        context['search_form'] = search_form
        context['point'] = point

        return context


class AddView(TemplateView):
    template_name = 'add.html'

    def post(self, *args, **kwargs):
        venue_form = VenueForm(self.request.POST or None, prefix='venue')
        event_form = EventForm(self.request.POST or None, prefix='event')
        organization_form = OrganizationForm(self.request.POST or None, prefix='organization')

        if venue_form.is_valid() and \
                event_form.is_valid() and \
                organization_form.is_valid():
            organization = organization_form.save()
            venue = venue_form.save()
            event = event_form.save(commit=False)
            event.host = organization
            event.venue = venue
            event.save()

            # todo: add a success message.

            return redirect('/')

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