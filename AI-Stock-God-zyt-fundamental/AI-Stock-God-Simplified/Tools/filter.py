import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# 设置tushare的API token
ts.set_token("xxx")
pro = ts.pro_api()

# 指定结束日期为20230403，并计算一个月前的日期
end_date = '20240620'
start_date = (datetime.strptime(end_date, '%Y%m%d') - timedelta(days=45)).strftime('%Y%m%d')

# 定义一个空的DataFrame来存储一个月内的数据
all_data = pd.DataFrame()

# 获取一个月内的每日数据
current_date = start_date
while current_date <= end_date:
    daily_data = pro.hsgt_top10(trade_date=current_date, market_type='1')
    every_data = pro.hsgt_top10(trade_date=current_date, market_type='3')
    daily_data = pd.concat([daily_data, every_data], ignore_index=True)
    if not daily_data.empty:
        all_data = pd.concat([all_data, daily_data], ignore_index=True)
    current_date = (datetime.strptime(current_date, '%Y%m%d') + timedelta(days=1)).strftime('%Y%m%d')

# 汇总每个公司的出现频率和总交易量
summary = all_data.groupby('ts_code').agg({
    'name': 'first',
    'amount': 'sum',
    'trade_date': 'count'
}).rename(columns={'trade_date': 'frequency'})

# 按出现频率排名
frequency_rank = summary.sort_values(by='frequency', ascending=False)

# 按总交易量排名
amount_rank = summary.sort_values(by='amount', ascending=False)

# 输出结果
print("按出现频率排名的前10家公司：")
print(frequency_rank.head(10))
print("\n按总交易量排名的前10家公司：")
print(amount_rank.head(10))