import json
import urllib

from datetime import datetime, timedelta
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic import DetailView, TemplateView

from .api import EventFilterBackend
from .forms import VenueForm, OrganizationForm, EventForm
from .models import Event, Organization, Venue


class EventDetailView(DetailView):
    template_name = 'event_detail.html'
    model = Event


class MapView(TemplateView):
    template_name = 'map.html'

    def get_context_data(self, **kwargs):
        context = super(MapView, self).get_context_data(**kwargs)

        event_filter_backend = EventFilterBackend()
        search_form = event_filter_backend.prepare_search_form(request=self.request)
        point = event_filter_backend.get_point(search_form['address'].value)
        context['events'] = event_filter_backend.filter_queryset(request=self.request, queryset=Event.objects.all(), view=self, search_form=search_form, point=point)
        
        context['now'] = datetime.now()
        context['future'] = datetime.now() + timedelta(days=int(search_form.data['days']))
        context['search_form'] = search_form
        context['point'] = point

        return context


class EmbedView(TemplateView):
    template_name = 'embed.html'


class EmbedDemoView(TemplateView):
    template_name = 'embed-demo.html'


class AddView(TemplateView):
    template_name = 'add.html'

    def post(self, *args, **kwargs):
        venue_form = VenueForm(self.request.POST or None, prefix='venue')
        event_form = EventForm(self.request.POST or None, prefix='event')
        organization_form = OrganizationForm(self.request.POST or None, prefix='organization')

        if (venue_form.data['venue-venue_id'] or venue_form.is_valid()) and \
                event_form.is_valid() and \
                (organization_form.data['organization-organization_id'] or organization_form.is_valid()):

            if venue_form.data['venue-venue_id']:
                venue = Venue.objects.get(pk=int(venue_form.data['venue-venue_id']))
            else:
                venue = venue_form.save()

            if organization_form.data['organization-organization_id']:
                organization = Organization.objects.get(pk=int(organization_form.data['organization-organization_id']))
            else:
                organization = organization_form.save()

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