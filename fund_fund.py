from  fund_mysql import db

def update_t5_value(cur,id,sm_time):
    db.ping(reconnect=True)
    cur.execute("select * from fund_commit where fund_id = %s and time > %f order by value desc limit 5" % (id, sm_time))
    db_fund_commit = cur.fetchall()
    db_fund_commit_t5_value = float(db_fund_commit[-1].get("value"))
    db.ping(reconnect=True)
    cur.execute("update fund set t5_value = %f   where id = %s" % (db_fund_commit_t5_value, id))
def update_b5_value(cur,id,sm_time):
    db.ping(reconnect=True)
    cur.execute("select * from fund_commit where fund_id = %s and time > %f order by value asc limit 5" % (id, sm_time))
    db_fund_commit = cur.fetchall()
    db_fund_commit_b5_value = float(db_fund_commit[-1].get("value"))
    db.ping(reconnect=True)
    cur.execute("update fund set b5_value = %f   where id = %s" % (db_fund_commit_b5_value, id))
def update_value(cur,id,sm_time):
    db.ping(reconnect=True)
    cur.execute("select * from fund_commit where fund_id = %s and time > %f order by time  desc  limit 1" % (id, sm_time))
    db_fund_commit = cur.fetchall()
    db_fund_commit_l1_value = float(db_fund_commit[0].get("value"))
    db.ping(reconnect=True)
    cur.execute("update fund set value = %f   where id = %s" % (db_fund_commit_l1_value, id))
def update_sm_rate(cur,id,sm_rate):
    db.ping(reconnect=True)
    cur.execute("update fund set sm_rate = %f   where id = %s" % (sm_rate, id))