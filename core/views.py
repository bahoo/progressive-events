from datetime import datetime, timedelta
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import TemplateView

from .forms import SearchForm
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

        point = get_point(address)

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


class WhyView(TemplateView):
    template_name = 'why.html'