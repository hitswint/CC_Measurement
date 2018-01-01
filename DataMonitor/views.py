# from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.conf import settings
from DataMonitor.models import GY_39_Category, GY_39
import logging
from django.views.decorators.csrf import csrf_exempt
# import sqlite3
# 查看tables：apt安装sqlite3，然后sqlite3 db.sqlite3，输入.tables。
import matplotlib.pyplot as plt
# import os
# matplotlib.use('Agg')
# import matplotlib

logger = logging.getLogger(__name__)

# Create your views here.


@csrf_exempt
def index(request):
    if request.method == 'POST':
        Sensor_name = request.POST.get("Sensor_name", "")

        if not GY_39_Category.objects.get(name=Sensor_name):
            add_GY_39_Category = GY_39_Category(
                name=Sensor_name,
                url=reverse('GY-39-view', args=(Sensor_name, )))
            add_GY_39_Category.save()

        add_GY_39 = GY_39(
            Category=GY_39_Category.objects.get(name=Sensor_name),
            # 若已知外键id，也可用id添加外键。
            # Category_id = the_Category_id
            Temperature=request.POST.get("T", ""),
            Humidity=request.POST.get("H", ""),
            Pressure=request.POST.get("P", ""),
            Luminance=request.POST.get("L", ""))
        add_GY_39.save()  # 不save无法保存到数据库
        return HttpResponse("OK!")
    else:
        GY_39_Category_list = GY_39_Category.objects.all()
        GY_39_list = [
            category_object.GY_39_set.order_by('Time').all()[0]
            for category_object in GY_39_Category_list
        ]
        return render_to_response('DataMonitor/index.html',
                                  {'GY_39_list': GY_39_list})


# def index_plot(request):
#     # 从sqlite中获取数据。
#     conn = sqlite3.connect('db.sqlite3')
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM TM_Temperature")
#     data = cur.fetchall()
#     data_0 = [int(row[0]) for row in data][-500:]
#     data_2 = [float(row[2]) for row in data][-500:]

#     plot_file = 'static/TM/plot.png'
#     fig1, ax1 = plt.subplots(figsize=(8, 4), dpi=98)
#     ax1.set_title(u'房间温度', fontproperties='KaiTi')
#     ax1.set_xlabel(u'时间(小时)', fontproperties='KaiTi')
#     ax1.set_ylabel(u'温度(\u2103)', fontproperties='KaiTi')
#     plt.ylim(-30, 30)
#     ax1.plot(
#         data_0,
#         data_2, )
#     fig1.savefig(plot_file)
#     plt.close(fig1)

#     # temperature_list = Temperature.objects.all()
#     return HttpResponse(plot_file)


# * Base_Mixin
class Base_Mixin(object):
    """Basic mix class."""

    def get_context_data(self, *args, **kwargs):
        context = super(Base_Mixin, self).get_context_data(**kwargs)
        try:
            # 网站标题等内容
            context['website_title'] = settings.WEBSITE_TITLE
        except Exception:
            logger.error(u'[BaseMixin]加载基本信息出错')
        return context


# * GY_39_View
class GY_39_View(Base_Mixin, ListView):
    """view for category.html"""
    template_name = 'DataMonitor/GY-39.html'
    context_object_name = 'GY_39_list'

    def get_queryset(self):
        category = self.kwargs.get('name', '')
        try:
            GY_39_list = GY_39_Category.objects.get(
                name=category).GY_39_set.all()
        except GY_39_Category.DoesNotExist:
            logger.error(u'[Category_View]此分类不存在:[%s]' % category)
            raise Http404

        return GY_39_list
