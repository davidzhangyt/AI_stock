import pandas as pd
import matplotlib.pyplot as plt
import tushare as ts
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

pd.set_option('expand_frame_repr', False)  # True就是可以换行显示。设置成False的时候不允许换行
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('colheader_justify', 'centre')  # 显示居中

ts.set_token('xx')

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
    end_date_dt = start_date_dt + relativedelta(months=1)
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
portfolio_status1 = {
        "cash": 29339,
        "stocks": [{'code': '600282.SH', 'name': 'Nanjing Steel United', 'shares': 5000, 'price': 3.91},
        {'code': '601857.SH', 'name': 'PetroChina Company Limited', 'shares': 3000, 'price': 6.00},
        {'code': '601012.SH', 'name': 'LONGi Green Energy Technology', 'shares': 500, 'price': 40.63},
        {'code': '002594.SZ', 'name': 'BYD Company Limited', 'shares': 50, 'price': 255.92}],
        "date": "20230403",
    }

portfolio_status2 = {
        "cash": 65124,
        "stocks": [{'code': '601857.SH', 'name': 'PetroChina Company Limited', 'shares': 3000, 'price': 7.89},
        {'code': '002594.SZ', 'name': 'BYD Company Limited', 'shares': 50, 'price': 255.86}],
        "date": "20230504"
    }

portfolio_status3 = {
        "cash": 35332,
        "stocks": [{'code': '601857.SH', 'name': 'PetroChina Company Limited', 'shares': 3000, 'price': 7.65},
        {'code': '002594.SZ', 'name': 'BYD Company Limited', 'shares': 165, 'price': 259.06}],
        "date": "20230602"
    }

portfolio_status4 = {
        "cash": 20350.48,
        "stocks": [{'code': '601857.SH', 'name': 'PetroChina Company Limited', 'shares': 3000, 'price': 7.82},
        {'code': '002594.SZ', 'name': 'BYD Company Limited', 'shares': 165, 'price': 267.48},
        {'code': '601012.SH', 'name': 'Longi Green Energy Technology', 'shares': 519, 'price': 28.88},],
        "date": "20230703"
    }

portfolio_status5 = {
        "cash": 11.59,
        "stocks": [{'code': '601857.SH', 'name': 'PetroChina Company Limited', 'shares': 1500, 'price': 7.58},
        {'code': '002594.SZ', 'name': 'BYD Company Limited', 'shares': 283, 'price': 268.23},
        {'code': '601012.SH', 'name': 'Longi Green Energy Technology', 'shares': 534, 'price': 30.85},],
        "date": "20230803"
    }

portfolio_status6 = {
        "cash": 11.59,
        "stocks": [{'code': '601857.SH', 'name': 'PetroChina Company Limited', 'shares': 1500, 'price': 7.76},
        {'code': '002594.SZ', 'name': 'BYD Company Limited', 'shares': 283, 'price': 249.12},
        {'code': '601012.SH', 'name': 'Longi Green Energy Technology', 'shares': 534, 'price': 26.58},],
        "date": "20230904"
    }

portfolio_status7 = {
        "cash": 47.01,
        "stocks": [{'code': '601012.SH', 'name': 'Longi Green Energy Technology', 'shares': 3405, 'price': 27.28},],
        "date": "20231009"
    }

portfolio_status8 = {
        "cash": 46.80,
        "stocks": [{'code': '688339.SH', 'name': 'SinoHytec', 'shares': 767, 'price': 50.75},
                   {'code': '300124.SZ', 'name': 'Shenzhen Inovance Technology', 'shares': 623, 'price': 62.47}],
        "date": "20231106"
    }
# portfolio_status9 = {
#         "cash": 46.80,
#         "stocks": [{'code': '688339.SH', 'name': 'SinoHytec', 'shares': 767, 'price': 53.6},
#                    {'code': '300124.SZ', 'name': 'Shenzhen Inovance Technology', 'shares': 623, 'price': 65.69}],
#         "date": "20231204"
#     }

# portfolio_status10 = {
#         "cash": 46.80,
#         "stocks": [{'code': '688339.SH', 'name': 'SinoHytec', 'shares': 767, 'price': 44.56},
#                    {'code': '300124.SZ', 'name': 'Shenzhen Inovance Technology', 'shares': 623, 'price': 61.05}],
#         "date": "20240103"
#     }

# portfolio_status11 = {
#         "cash": 4.35,
#         "stocks": [{'code': '600023.SH', 'name': 'Zhejiang Energy Group', 'shares': 4597, 'price': 5.41},
#                    {'code': '300124.SZ', 'name': 'Shenzhen Inovance Technology', 'shares': 623, 'price': 57.24}],
#         "date": "20240205"
#     }

# portfolio_status12 = {
#         "cash": 4.35,
#         "stocks": [{'code': '600023.SH', 'name': 'Zhejiang Energy Group', 'shares': 4597, 'price': 5.26},
#                    {'code': '300124.SZ', 'name': 'Shenzhen Inovance Technology', 'shares': 623, 'price': 63.85}],
#         "date": "20240304"
#     }

# portfolio_status13 = {
#         "cash": 4.35,
#         "stocks": [{'code': '600023.SH', 'name': 'Zhejiang Energy Group', 'shares': 4597, 'price': 6.7},
#                    {'code': '300124.SZ', 'name': 'Shenzhen Inovance Technology', 'shares': 623, 'price': 61.48}],
#         "date": "20240403"
#     }

# portfolio_status14 = {
#         "cash": 65715.16,
#         "stocks": [{}],
#         "date": "20240503"
#     }

# 回测每月投资组合并合并结果
portfolios = []
for portfolio_status in [portfolio_status1, portfolio_status2, portfolio_status3, portfolio_status4, portfolio_status5, portfolio_status6, portfolio_status7, portfolio_status8]:
    portfolio = backtest(portfolio_status)
    portfolios.append(portfolio)

# 合并所有月份的数据
combined_portfolio = pd.concat(portfolios)

# 获取大盘指数的模拟投资组合数据
start_date = min([portfolio_status1["date"], portfolio_status2["date"], portfolio_status3["date"], portfolio_status4["date"], portfolio_status5["date"], portfolio_status6["date"]])
end_date = (datetime.strptime(portfolio_status8["date"], "%Y%m%d") + relativedelta(months=1)).strftime("%Y%m%d")
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
