from django.conf.urls import url
from .views import MapView, WhyView

urlpatterns = [
    url(r'^$', MapView.as_view(), name='index'),
    url(r'^why$', WhyView.as_view(), name='why')
]
