from  fund_mysql import db
def update_hold(cur,id):
    db.ping(reconnect=True)
    cur.execute("select * from fund_hold  where id = %d" % (id))
    db_fund_hold = cur.fetchall()
    db_fund_id = str(db_fund_hold[0].get('fund_id'))
    db_fund_hold_share = float(db_fund_hold[0].get('share'))
    db_fund_hold_id =int(db_fund_hold[0].get('id'))
    # 获取value
    db.ping(reconnect=True)
    cur.execute("select  * from fund where id = %s " % (db_fund_id))
    db_fund = cur.fetchall()
    db_fund_value = float(db_fund[0].get('value'))
    # 获取交易中 hold
    db.ping(reconnect=True)
    cur.execute("select  sum(trade_history.hold) as hold from trade_history where fund_hold_id = %d and status in ('in-trading') group by fund_hold_id "  % (db_fund_hold_id))
    db_trade_history = cur.fetchall()
    print(db_trade_history)
    if db_trade_history:
        db_trade_history_hold = float(db_trade_history[0].get('hold'))
    else:
        db_trade_history_hold = 0

    # hold 计算
    hold = db_fund_hold_share * db_fund_value + db_trade_history_hold
    db.ping(reconnect=True)
    cur.execute("update fund_hold set hold = %f where id = %d " % (hold,db_fund_hold_id) )
    return  hold
def update_share(cur,id):
    db.ping(reconnect=True)
    cur.execute("select * from fund_hold  where id = %d" % (id))
    db_fund_hold = cur.fetchall()
    db_fund_hold_share = float(db_fund_hold[0].get('share'))
    # 获取最近已完成交易
    db.ping(reconnect=True)
    cur.execute("select sum(share) as share from trade_history   where fund_hold_id = %d  and status in ('out-trade','in-trade') " %  (id))
    db_trade_history = cur.fetchall()

    db_trade_history_share = float(db_trade_history[0].get('share'))
    # share 计算
    share = db_fund_hold_share + db_trade_history_share
    db.ping(reconnect=True)
    cur.execute("update fund_hold set share = %f where id = %d " % (share,id))
def update_cost_value(cur,id):
    db.ping(reconnect=True)
    cur.execute("select fund_hold.cost_value as cost_value , fund_hold.share as share   from fund_hold    where fund_hold.id = %d" % (id))
    db_fund_hold = cur.fetchall()
    db_fund_hold_share = float(db_fund_hold[0].get('share'))
    db_fund_hold_cost_value = float(db_fund_hold[0].get('cost_value'))
    # 计算交易
    db.ping(reconnect=True)
    cur.execute("select trade_history.hold as hold, trade_history.share as share from trade_history   where trade_history.fund_hold_id = %d  and trade_history.status in ('in-trade','out-trade') "  % (id) )
    db_trade_history = cur.fetchall()
    for th in db_trade_history:
        th_trade_history_hold = float(th.get('hold'))
        th_trade_history_share = float(th.get('share'))
        db_fund_hold_cost_value = (db_fund_hold_share *db_fund_hold_cost_value +th_trade_history_hold)/(db_fund_hold_share+th_trade_history_share)
    db.ping(reconnect=True)
    cur.execute("update fund_hold set cost_value = %f where id = %d " % (db_fund_hold_cost_value,id))
