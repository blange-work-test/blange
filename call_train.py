from fund_mysql import  db
import pymysql
import time
import requests
import re
import ast
from space import update_reinvest_modulus as space_update_reinvest_modulus
from space import  update_sum_product as space_update_sum_product
from space import update_hold as space_update_hold
from space import  update_hold_income as space_update_hold_income
from fund_hold import update_hold as fund_hold_update_hold
from fund_hold import  update_share as fund_hold_update_share
from fund_hold import update_cost_value as fund_hold_update_cost_value
from fund_fund import update_t5_value as fund_update_t5_value
from fund_fund import update_b5_value as fund_update_b5_value
from fund_fund import update_value as fund_update_value
from fund_fund import update_sm_rate as fund_update_sm_rate
def update_market_train(market_id,sm_rate):
    cur = db.cursor(pymysql.cursors.DictCursor)
    # market更新
    db.ping(reconnect=True)
    cur.execute("update market set sm_rate = %f where id = %s" % (sm_rate, market_id))
    # 关联space查询
    db.ping(reconnect=True)
    cur.execute(
        "select  space.id as space_id  from space where market_id = '%s' " % (market_id))
    db_space = cur.fetchall()
    # space 更新
    for s in db_space:
        space_update_reinvest_modulus(cur,int(s.get('space_id')))
    db.commit()
    db.close()
def add_trade_train(fund_hold_id,trae_day,trade_hold,trade_share,trade_status):
    cur = db.cursor(pymysql.cursors.DictCursor)
    # 信息准备
    # trade_history 更新
    print('dao')
    db.ping(reconnect=True)
    cur.execute("insert into trade_history ( `fund_hold_id` ,`day`, `hold` ,`share`,`status` ) values (%d,%d,%f,%f,'%s') "% (fund_hold_id,trae_day,trade_hold,trade_share,trade_status))
    trade_id = int(db.insert_id())
    # fund_hold更新
    if trade_status == 'in-trade':
        fund_hold_update_cost_value(cur,fund_hold_id)
    if trade_status in ['in-trade','out-trade']:
        fund_hold_update_share(cur,fund_hold_id)
    if trade_status in ['in-trading','in-trade','out-trade']:
        fund_hold_update_hold(cur,fund_hold_id)
    # 关联space查询
    db.ping(reconnect=True)
    cur.execute("select  *  from fund_hold where id = %d " % (fund_hold_id))
    db_space = cur.fetchall()
    db_space_id = int(db_space[0].get('space_id'))
    # space 更新
    if trade_status in ['in-trade','out-trade']:
        space_update_hold_income(cur,db_space_id)
    if trade_status in ['in-trading','in-trade','out-trading','out-trade']:
        space_update_hold(cur,db_space_id)
        space_update_sum_product(cur,db_space_id)
        space_update_reinvest_modulus(cur,db_space_id)
    # trade_history 销帐
    if trade_status in ['in-trade','out-trade']:
        db.ping(reconnect=True)
        cur.execute("update trade_history set status = 'end' where id= %d  " % (trade_id))
    db.commit()
    db.close()
def update_trade_train(trade_id,trade_hold,trade_share):
    cur = db.cursor(pymysql.cursors.DictCursor)
    db.ping(reconnect=True)
    cur.execute("select * from trade_history where id = %d " % (trade_id))
    db_trade_history = cur.fetchall()
    db_trade_history_status = str(db_trade_history[0].get('status'))
    db_trade_history_fund_hold_id = int(db_trade_history[0].get('fund_hold_id'))
    # trade_history 更新
    if db_trade_history_status == 'in-trading':
        db.ping(reconnect=True)
        cur.execute("update trade_history set share = %f,status = 'in-trade' where id = %d " % (trade_share,trade_id))
    if db_trade_history_status == 'out-trading':
        db.ping(reconnect=True)
        cur.execute("update trade_history set hold = %f ,status = 'out-trade' where id = %d " % (trade_hold, trade_id))
    # fund_hold 更新

    fund_hold_update_cost_value(cur, db_trade_history_fund_hold_id)
    fund_hold_update_share(cur, db_trade_history_fund_hold_id)
    fund_hold_update_hold(cur, db_trade_history_fund_hold_id)
    # 关联space查询
    db.ping(reconnect=True)
    cur.execute("select  *  from fund_hold where id = %d " % (db_trade_history_fund_hold_id))
    db_space = cur.fetchall()
    db_space_id = int(db_space[0].get('space_id'))
    # space 更新
    space_update_hold_income(cur, db_space_id)
    space_update_hold(cur, db_space_id)
    space_update_sum_product(cur, db_space_id)
    space_update_reinvest_modulus(cur, db_space_id)
    # trade_history 销帐

    db.ping(reconnect=True)
    cur.execute("update trade_history set status = 'end' where id = %d  " % (trade_id))
    db.commit()
    db.close()

def robot_train():
    cur = db.cursor(pymysql.cursors.DictCursor)
    # 获取fund_list
    db.ping(reconnect=True)
    cur.execute("select id from fund  order by created desc ")
    fund_list = cur.fetchall()
    for f in fund_list:
        fund_id = f.get('id')
        db.ping(reconnect=True)
        cur.execute("select * from fund_commit where fund_id = %s order by time desc limit 1" % (fund_id))
        release_value = cur.fetchall()
        release_value_time = release_value[0].get("time")
        print(release_value_time)
        # fund_commit 更新
        url = "https://fund.eastmoney.com/pingzhongdata/%s.js" % (fund_id)
        strhtml = requests.get(url)
        print(strhtml.text)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        sm_rate = float(re.findall(r"var[\s]*syl_6y[\s]*=[\s]*\"([\S]+)\"", strhtml.text)[0]) / 100
        print(sm_rate)

        value_list_str = re.findall(r'({"x":%s[\S]+])+;\/\*累计净值走势\*\/' % (str(release_value_time*1000)), strhtml.text)
        print(value_list_str)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        if len(value_list_str):

            value_list = ast.literal_eval('['+ value_list_str[0])
            print(value_list)
            for day in value_list:
                value_time = int(day.get("x")) / 1000
                value_value = float(day.get("y"))
                if len(release_value):
                    if value_time > release_value_time:
                        db.ping(reconnect=True)
                        cur.execute("insert into fund_commit (`fund_id`,`time`,`value`) values ('%s',%d,%f) " % (fund_id, value_time, value_value))

                else:
                    db.ping(reconnect=True)
                    cur.execute("insert into fund_commit (`fund_id`,`time`,`value`) values ('%s',%d,%f) " % (fund_id, value_time, value_value))

            sm_time = time.mktime(time.localtime()) - 15638400
            fund_update_t5_value(cur,fund_id,sm_time)
            fund_update_b5_value(cur,fund_id,sm_time)
            fund_update_value(cur,fund_id,sm_time)
            fund_update_sm_rate(cur,fund_id,sm_rate)
        # fund_hold 更新
        db.ping(reconnect=True)
        cur.execute("select * from fund_hold where fund_id = '%s' "% (fund_id))
        fund_hold_list = cur.fetchall()
        for h in fund_hold_list:
            fund_hold_id = int(h.get("id"))
            fund_hold_space_id = int(h.get("space_id"))
            fund_hold_update_hold(cur,fund_hold_id)
            space_list = []
            if fund_hold_space_id not in space_list:
                space_list.append(fund_hold_space_id)
    for s in space_list:
        space_update_hold(cur,s)
        space_update_hold_income(cur,s)
        space_update_reinvest_modulus(cur,s)
        space_update_sum_product(cur,s)
    db.commit()
    db.close()
