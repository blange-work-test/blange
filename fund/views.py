# v2.0 依赖-------------------------------------------------------------
import re
# v1.0 依赖-------------------------------------------------------------
from django.shortcuts import redirect
from django.shortcuts import render
import pymysql
import time
from call_train import update_market_train
from call_train import add_trade_train
from call_train import update_trade_train
from  call_train import robot_train
from  fund_hold import update_hold as fund_hold_update_hold
from fund_mysql import db
from sql_meta import  t5_value_percent as sql_t5_value_percent
from sql_meta import b5_value_percent as sql_b5_value_percent
from sql_meta import fund_hold_lj_diff_share  as sql_fund_hold_lj_diff_share
from sql_meta import fund_hold_lj_income as sql_fund_hold_lj_income
from sql_meta import type_name as sql_type_name
from sql_meta import fund_hold_lj_ideal_hold as sql_fund_hold_lj_ideal_hold
from sql_meta import fund_hold_lj_day_invest as sql_fund_hold_lj_day_invest
# v2.0 方法------------------------------------------------------------------
# index
def index(request):
    return redirect('http://127.0.0.1:8000/fund-holds/list-html')
# market
def market(request,market_id,action):
    r_method = request.method
    print(r_method)
    r_path = request.path
    # print(r_path)
    # print(market_id)
    # print(action)
    if r_method == 'GET':
        if action == 'update-html':
            cur = db.cursor(pymysql.cursors.DictCursor)
            db.ping(reconnect=True)
            cur.execute("select * from market where id =%s" % market_id)
            space = cur.fetchall()
            db.close()
            return render(request, 'market.html', space[0])


    if r_method == 'POST':
        r__method = str(request.POST.get('_method'))
        if r__method == 'PUT':
            r_sm_rate = float(request.POST.get('sm_rate', ''))
            update_market_train(market_id, r_sm_rate)
            return redirect('http://127.0.0.1:8000/')
# space
def space(request,space_id,action):
    r_method = request.method
    r_space_id = int(space_id)
    if r_method == 'GET':
        if action == 'update-html':
            cur = db.cursor(pymysql.cursors.DictCursor)
            db.ping(reconnect=True)
            cur.execute('select * from space where id = %d' % r_space_id)
            db_space = cur.fetchall()

            db.close()
            return render(request, 'space.html', db_space[0])
    if r_method == 'POST':
        r__method = str(request.POST.get('_method'))
        if r__method == 'PUT':
            r_income = float(request.POST.get('income', ''))
            r_principal = float(request.POST.get('principal', ''))
            cur = db.cursor(pymysql.cursors.DictCursor)
            db.ping(reconnect=True)
            cur.execute("update space set  principal = %f,income = %f where id = %d" % (r_principal, r_income, r_space_id))
            db.commit()
            db.close()
            return redirect('http://127.0.0.1:8000/')
# fund_holds
def fund_holds(request,action):
    r_method = request.method
    if r_method == 'GET':
        if action == 'list-html':
            cur = db.cursor(pymysql.cursors.DictCursor)
            # to be better
            space_id = 2
            db.ping(reconnect=True)
            cur.execute(
                "select  market.sm_rate as sm_rate  from space left join market  on space.market_id = market.id where space.id= %d " % (
                    space_id))
            db_market = cur.fetchall()
            db_market_sm_rate = int(db_market[0].get('sm_rate'))
            if db_market_sm_rate < -0.15:
                fund_hold_lj_day_invest = '0'
            else:
                fund_hold_lj_day_invest = 'cast(%s as decimal(10,2))' % sql_fund_hold_lj_day_invest

            db.ping(reconnect=True)
            sql = "select fund_hold.id  as id,\
                fund.value as value, \
                fund_id as fund_id, \
                fund.manager as manager,\
                fund.name as name,\
                fund.t5_value as t5_value ,\
                cast(%s*100 as decimal(10,2)) as t5_diff_value,\
                fund.b5_value as b5_value ,\
                cast(%s*100 as decimal(10,2)) as b5_diff_value,\
                cast(%s/4 as decimal(10,2)) as trade_share,\
                cast( fund_hold.hold as decimal(10,2)) as hold ,\
                cast(%s as decimal(10,2)) as income ,\
                fund.sm_rate as sm_rate ,\
                %s as type , \
                date_format(fund_hold.created,'%%Y-%%m-%%d %%H:%%i:%%s') as created ,\
                date_format(fund_hold.updated,'%%Y-%%m-%%d %%H:%%i:%%s') as updated, \
                cast(%s as decimal(10,2)) as ideal_hold,\
                %s as day_invest  \
                from fund_hold \
                left join fund on fund.id = fund_hold.fund_id \
                left join space on space.id = fund_hold.space_id  \
                where  space.id = %d \
                order by fund_hold.hold desc\
                     " % (
            sql_t5_value_percent, sql_b5_value_percent, sql_fund_hold_lj_diff_share, sql_fund_hold_lj_income,
            sql_type_name, sql_fund_hold_lj_ideal_hold, fund_hold_lj_day_invest, space_id)
            print(sql)
            cur.execute(sql)
            list = cur.fetchall()
            print(list)
            db.ping(reconnect=True)
            cur.execute("select * from space where id = 2 ")
            space_msg = cur.fetchall()
            db.close()
            return render(request, 'fund_holds.html', {'fund_hold_list': list, 'space_msg': space_msg[0],'action':action})
        if action == 'add-html':
            cur = db.cursor(pymysql.cursors.DictCursor)
            db.ping(reconnect=True)
            cur.execute("select * from space order by id desc ")
            space_list = cur.fetchall()
            db.ping(reconnect=True)
            cur.execute("select * from fund where market_id = '000300'")
            fund_list = cur.fetchall()

            db.close()
            return render(request, 'fund_holds.html',{'request_type': 'add', 'space_list': space_list, 'fund_list': fund_list,'action':action})
    if r_method == 'POST':
        r_space_id = int(request.POST.get('space_id', ''))
        r_fund_id = str(request.POST.get('fund_id', ''))
        r_type = str(request.POST.get('type', ''))
        cur = db.cursor(pymysql.cursors.DictCursor)

        # a-1 fund_hold基金添加
        db.ping(reconnect=True)
        cur.execute(
            "insert into fund_hold(space_id,fund_id,type,hold,income,sm_rate,share) values(%d,'%s','%s',0,0,0,0)" % (
            r_space_id, r_fund_id, r_type))
        db.commit()
        db.close()
        return redirect('http://127.0.0.1:8000/fund-holds/list-html')
# fund_hold
def fund_hold(request,fund_hold_id,action):
    r_method = request.method
    if r_method == 'GET':
        if action == 'update-html':
            id = request.GET.get('id', '')
            cur = db.cursor(pymysql.cursors.DictCursor)
            db.ping(reconnect=True)
            cur.execute(
                "select fund_hold.id as id ,fund.name as name, fund.sm_rate as sm_rate,(fund.value - fund_hold.cost_value)*fund_hold.share as income,fund_hold.hold as hold ,fund_hold.type as type,fund_hold.share as share ,fund_hold.cost_value as cost_value from fund_hold left join fund on fund.id = fund_hold.fund_id  where fund_hold.id = %d" % (
                    int(id)))
            fund_hold = cur.fetchall()
            print(fund_hold[0])
            db.close()
            return render(request, 'fund_hold.html', {'request_type': 'update', 'fund_hold': fund_hold[0]})
    if r_method == 'POST':
        r_id = int(request.POST.get('id', ''))
        r_type = str(request.POST.get('type', ''))
        r_cost_value = float(request.POST.get('cost_value', ''))
        r_share = float(request.POST.get('share', ''))
        cur = db.cursor(pymysql.cursors.DictCursor)

        # a-1 fund_hold基金更新
        db.ping(reconnect=True)
        cur.execute("update  fund_hold set type = '%s',cost_value = %f ,share = %f where id = %d" % (
        r_type, r_cost_value, r_share, r_id))
        fund_hold_update_hold(cur, r_id)
        db.commit()
        db.close()
        return redirect('http://127.0.0.1:8000/fund-holds/list-html')
# fund_hold_trades
def fund_hold_trades(request,fund_hold_id,action):
    r_method = request.method
    if r_method == 'GET':
        if action == 'list-html':
            id = int(request.GET.get('id', ''))
            cur = db.cursor(pymysql.cursors.DictCursor)
            db.ping(reconnect=True)
            cur.execute("select fund_hold.id as id ,\
                fund.name as name ,\
                fund_hold.hold as hold ,\
                (fund.value - fund_hold.cost_value)*fund_hold.share as income, \
                fund.sm_rate as sm_rate,\
                fund_hold.share as share,\
                fund_hold.cost_value as cost_value,\
                fund_hold.type as type  \
                from fund_hold left join fund on fund_hold.fund_id = fund.id where fund_hold.id = %d " % (id))
            fund_hold = cur.fetchall()
            print(fund_hold)
            db.ping(reconnect=True)
            cur.execute(
                "select trade_history.id as id ,FROM_UNIXTIME(trade_history.day,'%%Y-%%m-%%d') as day,trade_history.hold as hold ,trade_history.share as share,trade_history.status as status from trade_history where fund_hold_id = %d  order by trade_history.day desc" % (
                    id))
            trade_history = cur.fetchall()
            print(trade_history)
            db.close()
            return render(request, 'fund_hold_trades.html', {'fund_hold': fund_hold[0], 'trade_history': trade_history,'action':action})
        if action == 'add-html':
            id = request.GET.get('id', '')
            return render(request, 'fund_hold_trades.html', {'request_type': 'add', 'fund_hold_id': id,'action':action})
    if r_method == 'POST':
        # 请求信息获取
        r_id = int(request.POST.get('id', ''))
        r_trade_day = int(time.mktime(time.strptime(request.POST.get('day', ''), "%Y-%m-%d")))
        r_trade_share = float(request.POST.get('share', ''))
        r_trade_hold = float(request.POST.get('hold', ''))
        if r_trade_hold > 0:
            # 买入
            if r_trade_share > 0:
                r_trade_status = 'in-trade'
            else:
                r_trade_status = 'in-trading'
        else:
            if r_trade_hold < 0:
                r_trade_status = 'out-trade'
            else:
                r_trade_status = 'out-trading'

        # 增加交易
        add_trade_train(r_id, r_trade_day, r_trade_hold, r_trade_share, r_trade_status)
        return redirect('http://127.0.0.1:8000/fund-holds/%s/trades/list-html?id=%d' % (fund_hold_id,r_id))
# fund_hold_trade
def fund_hold_trade(request,fund_hold_id,trade_id,action):
    r_method = request.method
    if r_method == 'GET':
        if action == 'update-html':
            id = int(request.GET.get('id', ''))
            cur = db.cursor(pymysql.cursors.DictCursor)
            db.ping(reconnect=True)
            cur.execute("select  trade_history.fund_hold_id as fund_hold_id, \
                 trade_history.id as id, \
                 FROM_UNIXTIME(trade_history.day,'%%Y-%%m-%%d') as day, \
                 trade_history.hold as hold ,\
                 trade_history.share as share ,\
                 trade_history.status as status \
                 from trade_history \
                 where id = %d " % (id))
            trade = cur.fetchall()
            print(trade)
            db.close()
            return render(request, 'fund_hold_trade.html', {'request_type': 'update', 'trade_msg': trade[0]})
    if r_method == 'POST':
        # 请求信息获取
        r_id = int(request.POST.get('id', ''))
        r_fund_hold_id = int(request.POST.get('fund_hold_id', ''))
        r_trade_status = str(request.GET.get('status', ''))
        print(r_trade_status)
        if r_trade_status == 'in-trading':
            r_trade_hold = 0
            r_trade_share = float(request.POST.get('share', ''))
        else:
            r_trade_share = 0
            r_trade_hold = float(request.POST.get('hold', ''))
            print(r_trade_hold)
        update_trade_train(r_id, r_trade_hold, r_trade_share)
        return redirect('http://127.0.0.1:8000/fund-holds/%d/trades/list-html?id=%d' % (r_fund_hold_id,r_fund_hold_id))
# funds
def funds(request,action):
    r_method = request.method
    if r_method == 'GET':
        if action == 'list-html':
            cur = db.cursor(pymysql.cursors.DictCursor)
            db.ping(reconnect=True)
            cur.execute(
                "select id,name,manager,date_format(created,'%Y-%m-%d %H:%i:%s') as created ,date_format(updated,'%Y-%m-%d %H:%i:%s') as updated from fund where market_id= '000300'")
            results = cur.fetchall()
            print(results)
            db.close()
            return render(request, 'funds.html', {'fund': results,'action':action})
        if action == 'add-html':
            return render(request, 'funds.html', {'action':action})
        # 临时用GET请求实现
        if action == 'reptile':
            robot_train()
            return redirect('http://127.0.0.1:8000/fund-holds/list-html')
    if r_method == 'POST':
        r__method = str(request.POST.get('_method'))
        if r__method == 'POST':
            # r_id = request.POST.get('id', '')
            # r_name = request.POST.get('name', '')
            # r_manager = request.POST.get('manager', '')
            # cur = db.cursor(pymysql.cursors.DictCursor)
            # db.ping(reconnect=True)
            # cur.execute("insert into fund (id,name,manager,market_id) values ('%s','%s','%s','000300')" % (
            # str(r_id), str(r_name), str(r_manager)))
            # db.commit()
            # db.close()
            return redirect('http://127.0.0.1:8000/funds/list-html' )
        # 暂未实现页面触发
        if r__method == 'PUT':
            if action == 'reptile':
                robot_train()
                return redirect('http://127.0.0.1:8000/fund-holds/list-html')





# v1.0 方法------------------------------------------------------------------
# 返回基金列表
# def fund_list(request):
#     cur = db.cursor(pymysql.cursors.DictCursor)
#     db.ping(reconnect=True)
#     cur.execute("select id,name,manager,date_format(created,'%Y-%m-%d %H:%i:%s') as created ,date_format(updated,'%Y-%m-%d %H:%i:%s') as updated from fund where market_id= '000300'")
#     results = cur.fetchall()
#     print(results)
#     db.close()
#     return render(request, 'fund.html', {'fund': results})
# 添加基金
# def add_fund(request):
#     r_id =request.POST.get('id','')
#     r_name = request.POST.get('name', '')
#     r_manager = request.POST.get('manager', '')
#     cur = db.cursor(pymysql.cursors.DictCursor)
#     db.ping(reconnect=True)
#     cur.execute("insert into fund (id,name,manager,market_id) values ('%s','%s','%s','000300')"%(str(r_id),str(r_name),str(r_manager)) )
#     db.commit()
#     db.close()
#     return render(request, 'success.html')
# 返回添加基金表单
# def fund_add_form(request):
#     return render(request,'fund_form.html')
# 返回持有基金表单
# def fund_hold_list(request):
#     cur = db.cursor(pymysql.cursors.DictCursor)
#     # to be better
#     space_id = 2
#     db.ping(reconnect=True)
#     cur.execute("select  market.sm_rate as sm_rate  from space left join market  on space.market_id = market.id where space.id= %d " % (space_id))
#     db_market = cur.fetchall()
#     db_market_sm_rate = int(db_market[0].get('sm_rate'))
#     if db_market_sm_rate < -0.15 :
#         fund_hold_lj_day_invest ='0'
#     else:
#         fund_hold_lj_day_invest = 'cast(%s as decimal(10,2))'% sql_fund_hold_lj_day_invest
#
#
#     db.ping(reconnect=True)
#     sql= "select fund_hold.id  as id,\
#     fund.value as value, \
#     fund_id as fund_id, \
#     fund.manager as manager,\
#     fund.name as name,\
#     fund.t5_value as t5_value ,\
#     cast(%s*100 as decimal(10,2)) as t5_diff_value,\
#     fund.b5_value as b5_value ,\
#     cast(%s*100 as decimal(10,2)) as b5_diff_value,\
#     cast(%s/4 as decimal(10,2)) as trade_share,\
#     cast( fund_hold.hold as decimal(10,2)) as hold ,\
#     cast(%s as decimal(10,2)) as income ,\
#     fund.sm_rate as sm_rate ,\
#     %s as type , \
#     date_format(fund_hold.created,'%%Y-%%m-%%d %%H:%%i:%%s') as created ,\
#     date_format(fund_hold.updated,'%%Y-%%m-%%d %%H:%%i:%%s') as updated, \
#     cast(%s as decimal(10,2)) as ideal_hold,\
#     %s as day_invest  \
#     from fund_hold \
#     left join fund on fund.id = fund_hold.fund_id \
#     left join space on space.id = fund_hold.space_id  \
#     where  space.id = %d \
#     order by fund_hold.hold desc\
#          "%(sql_t5_value_percent,sql_b5_value_percent,sql_fund_hold_lj_diff_share,sql_fund_hold_lj_income,sql_type_name,sql_fund_hold_lj_ideal_hold,fund_hold_lj_day_invest,space_id)
#     print(sql)
#     cur.execute(sql)
#     list = cur.fetchall()
#     print(list)
#     db.ping(reconnect=True)
#     cur.execute("select * from space where id = 2 ")
#     space_msg = cur.fetchall()
#     db.close()
#     return  render(request,'fund_hold.html',{'fund_hold_list':list,'space_msg':space_msg[0]})
# 返回增加持有表单
# def fund_hold_add_form(request):
#
#     cur = db.cursor(pymysql.cursors.DictCursor)
#     db.ping(reconnect=True)
#     cur.execute("select * from space order by id desc " )
#     space_list = cur.fetchall()
#     db.ping(reconnect=True)
#     cur.execute("select * from fund where market_id = '000300'")
#     fund_list =cur.fetchall()
#
#     db.close()
#     return render(request, 'fund_hold_form.html', {'request_type': 'add', 'space_list':space_list, 'fund_list':fund_list})
# 返回添加交易表单
# def trade_add_form(request):
#     id = request.GET.get('id', '')
#     return render(request,'fund_hold_trade_form.html',{'request_type':'add','fund_hold_id':id})
# 返回添加交易表单
# def trade_update_form(request):
#     id = int(request.GET.get('id', ''))
#     cur = db.cursor(pymysql.cursors.DictCursor)
#     db.ping(reconnect=True)
#     cur.execute("select  trade_history.fund_hold_id as fund_hold_id, \
#      trade_history.id as id, \
#      FROM_UNIXTIME(trade_history.day,'%%Y-%%m-%%d') as day, \
#      trade_history.hold as hold ,\
#      trade_history.share as share ,\
#      trade_history.status as status \
#      from trade_history \
#      where id = %d " % (id))
#     trade =cur.fetchall()
#     print(trade)
#     db.close()
#     return render(request,'fund_hold_trade_form.html',{'request_type':'update','trade_msg':trade[0]})
# 添加持有
# def add_fund_hold(request):
#     r_space_id = int(request.POST.get('space_id',''))
#     r_fund_id = str(request.POST.get('fund_id', ''))
#     r_type = str(request.POST.get('type', ''))
#     cur = db.cursor(pymysql.cursors.DictCursor)
#
#     # a-1 fund_hold基金添加
#     db.ping(reconnect=True)
#     cur.execute("insert into fund_hold(space_id,fund_id,type,hold,income,sm_rate,share) values(%d,'%s','%s',0,0,0,0)" % (r_space_id,r_fund_id,r_type))
#     db.commit()
#     db.close()
#     return render(request,'success.html')
# 更新持有
# def update_fund_hold(request):
#     r_id = int(request.POST.get('id',''))
#     r_type = str(request.POST.get('type', ''))
#     r_cost_value = float(request.POST.get('cost_value',''))
#     r_share = float(request.POST.get('share', ''))
#     cur = db.cursor(pymysql.cursors.DictCursor)
#
#     # a-1 fund_hold基金更新
#     db.ping(reconnect=True)
#     cur.execute(        "update  fund_hold set type = '%s',cost_value = %f ,share = %f where id = %d" % (r_type, r_cost_value,r_share, r_id))
#     fund_hold_update_hold(cur,r_id)
#     db.commit()
#     db.close()
#     return redirect('http://127.0.0.1:8000/fund-hold/' )

# 返回更新基金表单
# def fund_hold_update_form(request):
#     id = request.GET.get('id','')
#     cur = db.cursor(pymysql.cursors.DictCursor)
#     db.ping(reconnect=True)
#     cur.execute("select fund_hold.id as id ,fund.name as name, fund.sm_rate as sm_rate,(fund.value - fund_hold.cost_value)*fund_hold.share as income,fund_hold.hold as hold ,fund_hold.type as type,fund_hold.share as share ,fund_hold.cost_value as cost_value from fund_hold left join fund on fund.id = fund_hold.fund_id  where fund_hold.id = %d" % (int(id)) )
#     fund_hold = cur.fetchall()
#     print(fund_hold[0])
#     db.close()
#     return  render(request, 'fund_hold_form.html', {'request_type': 'update', 'fund_hold': fund_hold[0]})
# 新增交易
# def add_trade(request):
#     # 请求信息获取
#     r_id = int(request.POST.get('id', ''))
#     r_trade_day = int(time.mktime(time.strptime(request.POST.get('day', ''),"%Y-%m-%d")))
#     r_trade_share = float(request.POST.get('share', ''))
#     r_trade_hold = float(request.POST.get('hold', ''))
#     if r_trade_hold > 0  :
#         # 买入
#         if r_trade_share > 0:
#             r_trade_status = 'in-trade'
#         else:
#             r_trade_status = 'in-trading'
#     else:
#         if r_trade_hold < 0:
#             r_trade_status = 'out-trade'
#         else:
#             r_trade_status = 'out-trading'
#
#     # 增加交易
#     add_trade_train(r_id,r_trade_day,r_trade_hold,r_trade_share,r_trade_status)
#     return redirect('http://127.0.0.1:8000/fund-hold/trade?id=%d'%(r_id))
# 更新交易
# def update_trade(request):
#     # 请求信息获取
#     r_id = int(request.POST.get('id', ''))
#     r_fund_hold_id = int(request.POST.get('fund_hold_id',''))
#     r_trade_status = str(request.GET.get('status',''))
#     print(r_trade_status)
#     if r_trade_status == 'in-trading' :
#         r_trade_hold = 0
#         r_trade_share = float(request.POST.get('share', ''))
#     else:
#         r_trade_share = 0
#         r_trade_hold = float(request.POST.get('hold', ''))
#         print(r_trade_hold)
#     update_trade_train(r_id,r_trade_hold,r_trade_share)
#     return redirect('http://127.0.0.1:8000/fund-hold/trade/?id=%d'%(r_fund_hold_id))
# 返回基金交易列表
# def trade_list(request):
#     id = int(request.GET.get('id', ''))
#     cur = db.cursor(pymysql.cursors.DictCursor)
#     db.ping(reconnect=True)
#     cur.execute("select fund_hold.id as id ,\
#     fund.name as name ,\
#     fund_hold.hold as hold ,\
#     (fund.value - fund_hold.cost_value)*fund_hold.share as income, \
#     fund.sm_rate as sm_rate,\
#     fund_hold.share as share,\
#     fund_hold.cost_value as cost_value,\
#     fund_hold.type as type  \
#     from fund_hold left join fund on fund_hold.fund_id = fund.id where fund_hold.id = %d " % (id))
#     fund_hold = cur.fetchall()
#     print(fund_hold)
#     db.ping(reconnect=True)
#     cur.execute("select trade_history.id as id ,FROM_UNIXTIME(trade_history.day,'%%Y-%%m-%%d') as day,trade_history.hold as hold ,trade_history.share as share,trade_history.status as status from trade_history where fund_hold_id = %d  order by trade_history.day desc" % (id))
#     trade_history = cur.fetchall()
#     print(trade_history)
#     db.close()
#     return render(request, 'fund_hold_trade.html', {'fund_hold': fund_hold[0],'trade_history':trade_history})
# 返回更新个人资料表单
# def space_update_form(request):
#     space_id = 2
#     cur = db.cursor(pymysql.cursors.DictCursor)
#     db.ping(reconnect=True)
#     cur.execute('select * from space where id = %d'% space_id )
#     db_space = cur.fetchall()
#
#     db.close()
#     return render(request,'space_form.html',db_space[0])
# def update_space(request):
#     r_id = int(request.POST.get('id', ''))
#     r_income = float(request.POST.get('income', ''))
#     r_principal = float(request.POST.get('principal', ''))
#     cur = db.cursor(pymysql.cursors.DictCursor)
#     db.ping(reconnect=True)
#     cur.execute("update space set  principal = %f,income = %f where id = %d" % (r_principal,r_income,r_id))
#     db.commit()
#     db.close()
#     return render(request, 'success.html')
# def market_update_form(request):
#     cur = db.cursor(pymysql.cursors.DictCursor)
#     db.ping(reconnect=True)
#     cur.execute("select * from market where id ='000300'")
#     space = cur.fetchall()
#     db.close()
#     return render(request, 'market_form.html', space[0])
# 市场更新
# def update_market(request):
#     r_id = int(request.POST.get('id', ''))
#     r_sm_rate = float(request.POST.get('sm_rate', ''))
#     update_market_train(r_id,r_sm_rate)
#     return redirect('http://127.0.0.1:8000/')
# def robot_update(request):
#     robot_train()
#     return redirect('http://127.0.0.1:8000/fund/' )
