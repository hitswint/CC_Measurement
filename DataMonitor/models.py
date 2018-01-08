from django.db import models


# * Sensor_type
class GY_39_Category(models.Model):
    """Documentation for Category"""
    name = models.CharField(unique=True, max_length=40, verbose_name=u'名字')
    url = models.CharField(
        max_length=200, blank=True, null=True, verbose_name=u'地址')
    create_time = models.DateTimeField(verbose_name=u'时间', auto_now_add=True)

    class Meta():
        ordering = [
            '-create_time',
        ]

    def __unicode__(self):
        return self.name

    __str__ = __unicode__


# * GY_39
class GY_39(models.Model):
    """Model for GY_39."""
    Category = models.ForeignKey(
        'GY_39_Category',
        on_delete=models.SET_DEFAULT,
        to_field='name',
        # null=True,
        default=u'Unknown',
        verbose_name=u'名字')
    Time = models.DateTimeField(verbose_name=u"时间", auto_now_add=True)
    Temperature = models.TextField(verbose_name=u"温度")
    Humidity = models.TextField(verbose_name=u"湿度")
    Pressure = models.TextField(verbose_name=u"压强")
    Luminance = models.TextField(verbose_name=u"照度")

    class Meta():
        ordering = [
            '-Time',
        ]

    def __unicode__(self):
        return self.Time

    __str__ = __unicode__
