#### fund_hold
### 虚拟属性
# v type_name->type
type_name = "(case fund_hold.type when 'auto_invest' then '定投' when 'clearance' then '清仓' when 'price_invest' then '定价投' else '错误类型' end )"
#### fund

### 虚拟属性

# v t5_value_percent->t5_value,value
t5_value_percent = '(fund.t5_value/fund.value-1)'
# v b5_value_percent->b5_value,value
b5_value_percent = '(fund.b5_value/fund.value-1)'
####space
### 虚拟属性
# v invest->reinvest_modulus,income,hold_income,principal
invest = '(space.principal+reinvest_modulus*(space.income-space.hold_income))'
# vv ideal_hold->invest, hold_income,hold
ideal_hold = '(%s*(space.hold/(space.hold-space.hold_income)))'%(invest)
#### fund_hold-LR-space-LR-fund
### 虚拟属性
# v income ->fund_hold.share,fund.value,fund_hold.cost_value
fund_hold_lj_income = '(fund_hold.share * (fund.value - fund_hold.cost_value))'
# v space_modulus->fund_hold.hold,space.hold
fund_hold_lj_space_modulus = '(case when fund_hold.hold > (space.hold * 0.2) then 0 else cast((1 - (fund_hold.hold/space.hold )) as decimal(10,4)) end )'
# v short_modulus->fund.sm_rate,fund_hold.created,space.hold_income,space.hold_income
fund_hold_lj_short_modulus = '(case when fund.sm_rate > 0 then (fund.sm_rate+0.2) else (case when (UNIX_TIMESTAMP(now())-UNIX_TIMESTAMP(fund_hold.created)) > 15768000 then 0 else(case when space.hold_income < 0 then 0 else cast(space.hold_income/space.hold as decimal(10,2) )end ) end  ) end)'
# v long_modulus->fund_hold.share,fund.value,fund_hold.cost_value,fund_hold.hold
fund_hold_lj_long_modulus = '(case when fund_hold.share = 0 then 0 when (fund_hold.share * (fund.value-fund_hold.cost_value)) < (-0.2*fund_hold.hold) then 0 else ((fund_hold.share * (fund.value-fund_hold.cost_value)) /fund_hold.hold +0.2) end)'
# vv product->space_modulus,short_modulus,long_modulus
fund_hold_lj_product = "(case when fund_hold.type in ('clearance','price_invest') then 0 else (%s*%s*%s) end )"%(fund_hold_lj_space_modulus,fund_hold_lj_short_modulus,fund_hold_lj_long_modulus)
# vvv product_percent-> product,space.sum_product
fund_hold_lj_product_percent = '(%s/space.sum_product)'% (fund_hold_lj_product)
# vvvv ideal_hold->product_percent,sapce.space_ideal_hold
fund_hold_lj_ideal_hold = '(%s*%s)'%(fund_hold_lj_product_percent,ideal_hold)
# vvvv day_invest->fund_hold_lj_product_percent,ideal_hold
fund_hold_lj_day_invest ='(%s*%s/120)'%(fund_hold_lj_product_percent,ideal_hold)
# vvvvv diff_share->fund_hold.hold,ideal_hoid,fund_hold.share
fund_hold_lj_diff_share = '((1-%s/fund_hold.hold)*fund_hold.share)'%(fund_hold_lj_ideal_hold)



