from django.conf.urls import url
from DataMonitor.views import index, GY_39_View, OtaVersionView, OtaUpdateView
# from swint.models import Article, Category

urlpatterns = [
    url(r'^$', index, name='index-view'),
    url(r'^GY_39/(?P<name>\w+)/$', GY_39_View.as_view(), name='GY-39-view'),
    url(r'^Fota/(?P<Sensor_name>\w+).version$',
        OtaVersionView.as_view(),
        name='ota-version-view'),
    url(r'^Fota/(?P<Sensor_name>\w+).bin$',
        OtaUpdateView.as_view(),
        name='ota-update-view'),
]
