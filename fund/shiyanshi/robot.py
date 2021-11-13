import requests        #导入requests包
import re
import ast
import time

from bs4 import    BeautifulSoup
url='https://fund.eastmoney.com/pingzhongdata/009076.js'
strhtml=requests.get(url)

fund_id = re.findall(r"var[\s]*fS_code[\s]*=[\s]*\"([\S]+)\"",strhtml.text)[0]
sm_rate = float(re.findall(r"var[\s]*syl_6y[\s]*=[\s]*\"([\S]+)\"",strhtml.text)[0])/100
value_list = ast.literal_eval(re.findall(r"var[\s]*Data_netWorthTrend[\s]*=[\s]*([\S]+);",strhtml.text)[0])
value_time = time.localtime(float(value_list[0].get("x"))/1000)
print(strhtml.text)
print(sm_rate)
print(value_time)
print(time.strftime("%Y-%m-%d",value_time))
print(type(time.time()))
