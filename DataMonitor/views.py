# from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic import ListView
from django.conf import settings
from DataMonitor.models import GY_39_Category, GY_39
import logging
from django.views.decorators.csrf import csrf_exempt
import sqlite3
# from django.utils import timezone
# import pytz
# import time
from datetime import datetime, timedelta, timezone
# 查看tables：apt安装sqlite3，然后sqlite3 db.sqlite3，输入.tables。
# import os
import matplotlib
# 若不加，服务器运行显示no display name and no $display environment variable。
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # 需在上句后引用。

logger = logging.getLogger(__name__)

# Create your views here.


@csrf_exempt
def index(request):
    if request.method == 'POST':
        Sensor_name = request.POST.get("Sensor_name", "")

        try:
            GY_39_Category.objects.get(name=Sensor_name)
        except GY_39_Category.DoesNotExist:
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
            category_object.gy_39_set.order_by('-Time').all()[0]
            for category_object in GY_39_Category_list
        ]
        return render_to_response('DataMonitor/index.html',
                                  {'GY_39_list': GY_39_list})


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

    def get(self, request, *args, **kwargs):
        category_name = self.kwargs.get('name', '')
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        # 通过sqlite3查询可知，外键项名称为Category_id，但值为to_field指定。
        cur.execute(
            'SELECT * FROM DataMonitor_gy_39 WHERE Category_id=:category_name',
            {'category_name': category_name})

        data = cur.fetchall()
        data_i = range(len([int(row[0]) for row in data]))[-288:]

        # 处理时间有time和datetime两个模块，后者更好用。
        # 先把str转为time类型，再转成需要的str。
        # data_Time = [
        #     time.strftime('%m/%d\n%H:%M', (time.strptime(
        #         row[1].split('.')[0], '%Y-%m-%d %H:%M:%S'))) for row in data
        # ][-20:]
        # 取数据库里的时间str，转化为datetime，并强制添加utc时区信息，再转换为local时区。
        data_Time = [
            datetime.strptime(
                row[1].split('.')[0], '%Y-%m-%d %H:%M:%S').replace(
                    tzinfo=timezone.utc).astimezone(
                        timezone(timedelta(hours=8))).strftime('%m/%d\n%H:%M')
            for row in data
        ][-288:]
        data_T = [float(row[2]) for row in data][-288:]
        data_H = [float(row[3]) for row in data][-288:]
        data_P = [float(row[4]) for row in data][-288:]
        data_L = [float(row[5]) for row in data][-288:]

        plot_file = 'static/DataMonitor/{}.png'.format(category_name)
        fig = plt.figure(figsize=(19, 8), dpi=98)
        ax1 = fig.add_subplot(221)
        ax2 = fig.add_subplot(222)
        ax3 = fig.add_subplot(223)
        ax4 = fig.add_subplot(224)
        # p1 = plt.subplot(221)
        # p2 = plt.subplot(222)
        # p3 = plt.subplot(223)
        # p4 = plt.subplot(224)

        # p1.set_title(u'温度', fontproperties='KaiTi')
        ax1.set_xlabel(u'Time(10min)', fontproperties='KaiTi')
        ax1.set_ylabel(u'Temperature(\u2103)', fontproperties='KaiTi')
        ax1.set_xticks(data_i[::12])
        ax1.set_xticklabels(data_Time[::12])
        # plt.ylim(-30, 30)
        ax1.plot(data_i, data_T, 'r:o', linewidth=1.2)

        # p2.set_title(u'湿度', fontproperties='KaiTi')
        ax2.set_xlabel(u'Time(10min)', fontproperties='KaiTi')
        ax2.set_ylabel(u'Humidity(%)', fontproperties='KaiTi')
        ax2.set_xticks(data_i[::12])
        ax2.set_xticklabels(data_Time[::12])
        # plt.ylim(-30, 30)
        ax2.plot(data_i, data_H, 'b--s', linewidth=1.2)

        # p3.set_title(u'压力', fontproperties='KaiTi')
        ax3.set_xlabel(u'Time(10min)', fontproperties='KaiTi')
        ax3.set_ylabel(u'Pressure(P)', fontproperties='KaiTi')
        ax3.set_xticks(data_i[::12])
        ax3.set_xticklabels(data_Time[::12])
        # plt.ylim(-30, 30)
        ax3.plot(data_i, data_P, 'g-.*', linewidth=1.2)

        # p4.set_title(u'光照', fontproperties='KaiTi')
        ax4.set_xlabel(u'Time(10min)', fontproperties='KaiTi')
        ax4.set_ylabel(u'Luminance(L)', fontproperties='KaiTi')
        ax4.set_xticks(data_i[::12])
        ax4.set_xticklabels(data_Time[::12])
        # plt.ylim(-30, 30)
        ax4.plot(data_i, data_L, 'y-d', linewidth=1.2)

        fig.tight_layout()
        fig.savefig(plot_file)
        plt.close(fig)

        return super(GY_39_View, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        kwargs['Category_name'] = self.kwargs.get('name', '')
        kwargs['plot_file'] = 'DataMonitor/{}.png'.format(
            self.kwargs.get('name', ''))
        return super(GY_39_View, self).get_context_data(**kwargs)

    def get_queryset(self):
        category = self.kwargs.get('name', '')
        try:
            GY_39_list = GY_39_Category.objects.get(
                name=category).gy_39_set.order_by('-Time').all()
        except GY_39_Category.DoesNotExist:
            logger.error(u'[Category_View]此分类不存在:[%s]' % category)
            raise Http404

        return GY_39_list
