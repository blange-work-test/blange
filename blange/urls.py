"""blange URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# v2.0方法
from fund.views import market,space,fund_holds,index,fund_hold,fund_hold_trades,fund_hold_trade,funds
from django.urls import path,re_path
# v1.0 方法
from django.contrib import admin
# from django.urls import path



urlpatterns = [
    # v2.0 路由
    path('', index),
    re_path(r'^funds/[\/]?(?P<action>[a-z0-9-]*)[\/]?', funds),
    re_path(r'^fund-holds/(?P<fund_hold_id>[0-9]+)/trades/(?P<trade_id>[0-9]+)[\/]?(?P<action>[a-z0-9-]*)[\/]?',fund_hold_trade),
    re_path(r'^fund-holds/(?P<fund_hold_id>[0-9]+)/trades[\/]?(?P<action>[a-z0-9-]*)[\/]?',fund_hold_trades),
    re_path(r'^fund-holds/(?P<fund_hold_id>[0-9]+)[\/]?(?P<action>[a-z0-9-]*)[\/]?',fund_hold),
    re_path(r'^fund-holds[\/]?(?P<action>[a-z0-9-]*)[\/]?',fund_holds),
    re_path(r'^markets/(?P<market_id>[0-9]+)[\/]?(?P<action>[a-z0-9-]*)[\/]?', market),
    re_path(r'^spaces/(?P<space_id>[0-9]+)[\/]?(?P<action>[a-z0-9-]*)[\/]?',space),
    # v1.0 路由
    # path('', fund_hold_list),
    path('admin/', admin.site.urls),
    # path('fund/',fund_list),
    # path('fund/robot-update/post',robot_update),
    # path('fund/add-form/',fund_add_form),
    # path('fund/add-form/post',add_fund),
    # path('fund-hold/',fund_hold_list),
    # path('fund-hold/add-form/',fund_hold_add_form),
    # path('fund-hold/update-form',fund_hold_update_form),
    # path('fund-hold/update-form/post',update_fund_hold),
    # path('fund-hold/add-form/post',add_fund_hold),
    # path('fund-hold/trade/',trade_list),
    # path('fund-hold/trade/add-form/',trade_add_form),
    # path('fund-hold/trade/update-form/',trade_update_form),
    # path('fund-hold/trade/add-form/post',add_trade),
    # path('fund-hold/trade/update-form/post',update_trade),


    # path('space/update-form/',space_update_form),
    # path('space/update-form/post',update_space),
    # path('market/update-form/',market_update_form),
    # path('market/update-form/post',update_market),

]
