# restapi：
## market

### :market_id`market`

- `GET markets/:market_id/update-html`:获取更新市场的html
- `PUT markets/:market_id`:更新市场

## space

### :sapce_id`space`

- `GET spaces/:space_id/update-html `:获取更新空间html
- `PUT spaces/:space_id`:更新空间

## fund_hold

### fund_holds`fund_holds`

- `GET fund_holds/list-html`:获取基金持有列表html
- `GET fund_holds/add-html`: 获取新增基金持有html
- `POST fund_holds`:新增基金持有

### :fund_hold_id`fund_hold`

- `GET fund_holds/:fund_hold_id/update-html`：获取更新基金持有html
- `PUT fund_holds/:fund_hold_id`：更新基金持有

#### trade

##### Trades`fund_hold_trades`

- `GET fund_holds/:fund_hold_id/trades/list-html`:获取基金持有的交易记录html
- `GET fund_holds/:fund_hold_id/trades/add-html`:获取新增基金持有的交易记录html
- `POST fund_holds/:fund_hold_id/trades`:新增基金持有的交易记录

##### :trade_id`fund_hold_trade`

- `GET fund_holds/:fund_hold_id/trades/:trade_id/update-html`:获取更新基金持有的交易记录html
- `PUT fund_holds/:fund_hold_id/trades/:trade_id`:更新基金持有的交易记录

## fund

### funds`funds`

- `GET funds/add-html`:获取新增基金html
- `GET funds/list-html`:获取基金列表html

- `GET funds/reptile`:爬虫更新基金数据
- `POST funds`:新增基金
# todo



