from django.conf.urls import include, url
from django.views.i18n import javascript_catalog

import api
import views


js_info_dict = {
    'packages': ('recurrence', ),
}

urlpatterns = [
    url(r'^$', views.MapView.as_view(), name='index'),
    url(r'^why$', views.WhyView.as_view(), name='why'),
    url(r'^add$', views.AddView.as_view(), name='add'),

    # experimental embed view
    url(r'^embed$', views.EmbedView.as_view(), name='embed'),
    url(r'^embed-test$', views.EmbedTestView.as_view(), name='embed-test'),
    
    url(r'^api/1/events', api.EventList.as_view()),
    url(r'^api/1/orgs', api.OrganizationList.as_view()),
    url(r'^api/1/venues', api.VenueList.as_view()),

    url(r'^events/(?P<slug>[\w\-]+)$', views.EventDetailView.as_view(), name='event_detail'),

    url(r'^jsi18n/$', javascript_catalog, js_info_dict)
]
