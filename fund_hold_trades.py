from  fund_mysql import db
# 更改交易状态
def reset_status(cur,fund_hold_id,status):
    try:
        # 待优化成枚举校验
        print('____________________')
        if  status == 'end':
            db.ping(reconnect=True)
            cur.execute("update trade_history set status = 'end' where fund_hold_id = %d "% (fund_hold_id))
        else:
            errormsg = "status只支持传入'end'"
            print(errormsg)

    except:
        errormsg = "请求失败"
        print(errormsg)


