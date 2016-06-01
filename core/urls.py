from django.conf.urls import url
from .views import AddView, MapView, WhyView

urlpatterns = [
    url(r'^$', MapView.as_view(), name='index'),
    url(r'^why$', WhyView.as_view(), name='why'),
    url(r'^add$', AddView.as_view(), name='add')

]
