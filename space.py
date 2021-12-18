from fund_mysql import db
from sql_meta import fund_hold_lj_product as product
def update_sum_product(cur,space_id):
    print(space_id)
    db.ping(reconnect=True)
    cur.execute(" select sum(%s)   as sum_product  \
                                from fund_hold \
                            left join space on space.id = fund_hold.space_id \
                left join fund on fund.id = fund_hold.fund_id \
                                where fund_hold.type != 'clearance'  and space.id = %d " \
                % (product, space_id) \
                )
    db_space = cur.fetchall()
    print(db_space)
    sum_product = float(db_space[0].get('sum_product'))
    db.ping(reconnect=True)
    cur.execute("update space set sum_product = %f where id = %d " % (sum_product, space_id))
    return sum_product
def update_reinvest_modulus(cur,space_id):
    db.ping(reconnect=True)
    cur.execute("select market.sm_rate as sm_rate ,space.hold_income as hold_income,space.hold as hold from space left join market on market.id = space.market_id where space.id = %d " % (space_id))
    db_space_market = cur.fetchall()
    db_market_sm_rate = db_space_market[0].get('sm_rate')
    db_space_hold_income  = db_space_market[0].get('hold_income')
    db_space_hold = db_space_market[0].get('hold')
    if db_market_sm_rate < 0 or db_space_hold_income < 0:
        reinvest_modulus = 0
    else:
        space_product = (db_market_sm_rate * db_space_hold_income) / (db_space_hold * 0.04)
        if space_product > 1:
            reinvest_modulus = 1
        else:
            reinvest_modulus = space_product
    db.ping(reconnect=True)
    cur.execute(
        "update space set reinvest_modulus = %f where id = %d " % (float(reinvest_modulus), space_id))
    return  reinvest_modulus

def update_hold(cur,space_id):
    db.ping(reconnect=True)
    cur.execute("select sum(hold) as space_hold from  fund_hold where space_id = %d "% (space_id) )
    db_fund_hold = cur.fetchall()
    db_space_hold = float(db_fund_hold[0].get('space_hold'))
    db.ping(reconnect=True)
    cur.execute("update space set hold = %f where id = %d " % (db_space_hold,space_id) )
    return  db_space_hold


def update_hold_income(cur,space_id):
    db.ping(reconnect=True)
    cur.execute("select sum((fund.value - fund_hold.cost_value)  * fund_hold.share) as space_hold_income \
    from fund_hold \
    left join fund on fund.id = fund_hold.fund_id \
    where fund_hold.space_id = %d" % (space_id)  )
    db_fund_hold =cur.fetchall()
    db_space_hold_income = float(db_fund_hold[0].get('space_hold_income'))
    db.ping(reconnect=True)
    cur.execute("update space set hold_income = %f where id = %d " % (db_space_hold_income, space_id))
