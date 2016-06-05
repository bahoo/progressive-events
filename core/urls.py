from django.conf.urls import url
from django.views.i18n import javascript_catalog
from .views import AddView, EventDetailView, MapView, VenueAPIView, WhyView

js_info_dict = {
    'packages': ('recurrence', ),
}

urlpatterns = [
    url(r'^$', MapView.as_view(), name='index'),
    url(r'^why$', WhyView.as_view(), name='why'),
    url(r'^add$', AddView.as_view(), name='add'),
    url(r'^api/1/venues', VenueAPIView.as_view(), name='venue_api'),
    url(r'^(?P<slug>[\w\-]+)$', EventDetailView.as_view(), name='event_detail'),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict)
]
