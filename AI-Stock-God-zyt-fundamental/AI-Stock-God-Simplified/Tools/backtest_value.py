import pandas as pd
import matplotlib.pyplot as plt
import tushare as ts
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

pd.set_option('expand_frame_repr', False)  # True就是可以换行显示。设置成False的时候不允许换行
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('colheader_justify', 'centre')  # 显示居中

ts.set_token('xxx')

def get_price(ts_code, start_date, end_date):
    pro = ts.pro_api()
    return pro.query('daily', ts_code=ts_code, start_date=start_date, end_date=end_date)

def get_index_price(ts_code, start_date, end_date):
    pro = ts.pro_api()
    return pro.index_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

def backtest(stock_info):
    total_cash = stock_info["cash"]
    start_date = stock_info["date"]
    start_date_dt = datetime.strptime(start_date, "%Y%m%d")
    end_date_dt = start_date_dt + relativedelta(months=12)
    end_date = end_date_dt.strftime("%Y%m%d")
    
    # 获取所有股票的历史价格数据
    stock_data = {}
    for stock in stock_info["stocks"]:
        ts_code = stock["code"]
        purchase_price = stock["price"]
        data = get_price(ts_code, start_date, end_date)
        data.sort_values('trade_date', inplace=True)
        data.set_index('trade_date', inplace=True)
        data.index = pd.to_datetime(data.index)  # 确保索引为Timestamp类型
        stock_data[ts_code] = data['close']
    
    # 创建一个投资组合数据表，包含所有股票的市值
    all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    portfolio = pd.DataFrame(index=all_dates)
    
    for ts_code, data in stock_data.items():
        portfolio[ts_code] = data.reindex(all_dates, method='ffill')
        
    # 计算持仓市值和总资产
    positions = pd.DataFrame(index=all_dates).fillna(0.0)
    for stock in stock_info["stocks"]:
        ts_code = stock["code"]
        purchase_amount = stock["shares"]
        initial_price = stock["price"]
        positions[ts_code] = purchase_amount
    
    portfolio['holding_values'] = positions.multiply(portfolio, axis=0).sum(axis=1) + stock_info["cash"]
    
    return portfolio

def get_index_portfolio(ts_code, start_date, end_date, initial_cash=100000):
    data = get_index_price(ts_code, start_date, end_date)
    data.sort_values('trade_date', inplace=True)
    data.set_index('trade_date', inplace=True)
    data.index = pd.to_datetime(data.index)  # 确保索引为Timestamp类型
    initial_price = data['close'].iloc[0]
    shares = initial_cash / initial_price
    data['index_value'] = shares * data['close']
    return data['index_value']

# 定义每月的投资组合
# portfolio_status1 = {
#         "cash": 1884.84,
#         "stocks": [{'code': '600519.SH', 'name': '贵州茅台', 'shares': 13, 'price': 1802.07},
#         {'code': '600036.SH', 'name': '招商银行', 'shares': 436, 'price': 34.37},
#         {'code': '300750.SZ', 'name': '宁德时代', 'shares': 62, 'price': 398.71},
#         {'code': '601012.SH', 'name': '隆基绿能', 'shares': 492, 'price': 40.63},
#         {'code': '300059.SZ', 'name': '东方财富', 'shares': 655, 'price': 22.89}],
#         "date": "20230403",
#     }
portfolio_status1 = {
        "cash": 428.27,
        "stocks": [{'code': '600519.SH', 'name': '贵州茅台', 'shares': 11, 'price': 1802.07},
        {'code': '000858.SZ', 'name': '五粮液', 'shares': 102, 'price': 195.19},
        {'code': '300750.SZ', 'name': '宁德时代', 'shares': 50, 'price': 398.71},
        {'code': '601012.SH', 'name': '隆基绿能', 'shares': 492, 'price': 40.63},
        {'code': '601888.SH', 'name': '中国中免', 'shares': 108, 'price': 184.39}],
        "date": "20230403",
    }


# 回测每月投资组合并合并结果
portfolios = []
for portfolio_status in [portfolio_status1]:
    portfolio = backtest(portfolio_status)
    portfolios.append(portfolio)

# 合并所有月份的数据
combined_portfolio = pd.concat(portfolios)

# 获取大盘指数的模拟投资组合数据
start_date = min([portfolio_status1["date"]])
end_date = (datetime.strptime(portfolio_status1["date"], "%Y%m%d") + relativedelta(months=12)).strftime("%Y%m%d")
index_portfolio = get_index_portfolio('399300.SZ', start_date, end_date, initial_cash=100000)

# 绘制总资产和持仓股票市值曲线图以及大盘模拟投资组合
plt.figure(figsize=(18, 10))
plt.plot(combined_portfolio.index, combined_portfolio['holding_values'], '--', label='Portfolio Market Value')
plt.plot(index_portfolio.index, index_portfolio, label='HS300 Index Value', color='red')
plt.legend()
plt.grid()
plt.xlabel('Date')
plt.ylabel('Value (RMB)')
plt.title('Portfolio Value and HS300 Index Over Time')
plt.ylim(0, 110000)  # 设置纵轴的范围为0到100000
plt.show()
