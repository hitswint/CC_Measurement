from django.conf.urls import url
from DataMonitor.views import index, GY_39_View
# from swint.models import Article, Category

urlpatterns = [
    url(r'^$', index, name='index-view'),
    url(r'^GY_39/(?P<name>\w+)/$',
        GY_39_View.as_view(),
        name='GY-39-view'),
]
