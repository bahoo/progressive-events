from django.conf.urls import url
from django.views.i18n import javascript_catalog
from .views import AddView, MapView, WhyView

js_info_dict = {
    'packages': ('recurrence', ),
}

urlpatterns = [
    url(r'^$', MapView.as_view(), name='index'),
    url(r'^why$', WhyView.as_view(), name='why'),
    url(r'^add$', AddView.as_view(), name='add'),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict)
]
