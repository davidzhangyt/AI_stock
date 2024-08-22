import pandas as pd
import matplotlib.pyplot as plt
import tushare as ts
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

pd.set_option('expand_frame_repr', False)  # True就是可以换行显示。设置成False的时候不允许换行
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.max_rows', None)  # 显示所有行
pd.set_option('colheader_justify', 'centre')  # 显示居中

ts.set_token('xxs')

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
    "cash": 0.74,
    "stocks": [{'code': '688235.SH', 'name': '百济恒瑞', 'shares': 647, 'price': 154.58}],
    "date": "20230410"
}

portfolio_status2 = {
    "cash": 73745.74,
    "stocks": [{'code': '688235.SH', 'name': '百济恒瑞', 'shares': 147, 'price': 147.49}],
    "date": "20230509"
}

portfolio_status3 = {
    "cash": 23810.19,
    "stocks": [{'code': '688235.SH', 'name': '百济恒瑞', 'shares': 147, 'price': 147.49},
               {'code': '002230.SZ', 'name': 'Irisity AB', 'shares': 753, 'price': 66.35}],
    "date": "20230609"
}

portfolio_status4 = {
    "cash": 12697.69,
    "stocks": [{"code": "688235.SH", "name": "百济恒瑞", "shares": 147, "price": 147.49},
               {"code": "002230.SZ", "name": "Irisity AB", "shares": 753, "price": 66.35},
               {"code": "300750.SZ", "name": "CATL", "shares": 50, "price": 222.25}],
    "date": "20230710"
}

portfolio_status5 = {
    "cash": 200.39,
    "stocks": [{"code": "002230.SZ", "name": "Irisity AB", "shares": 909, "price": 63.95},
               {"code": "300750.SZ", "name": "CATL", "shares": 132, "price": 247.00}],
    "date": "20230809"
}

portfolio_status6 = {
    "cash": 203.70,
    "stocks": [{"code": "601318.SH", "name": "Ping An Insurance", "shares": 499, "price": 50.12},
               {"code": "601012.SH", "name": "LONGi Green Energy Technology", "shares": 950, "price": 26.32},
               {"code": "002594.SZ", "name": "BYD", "shares": 100, "price": 244.05}],
    "date": "20230911"
}

portfolio_status7 = {
        "cash": 23805.33,
        "stocks": [{'code': '601012.SH', 'name': 'LONGi Green Energy Technology', 'shares': 1843, 'price': 27.10}],
        "date": "20231009"
    }

portfolio_status8 = {
        "cash": 34.17,
        "stocks": [{'code': '601012.SH', 'name': 'LONGi Green Energy Technology', 'shares': 1843, 'price': 24.24}
                    , {'code': '600196.SH', 'name': 'Fosun Pharmaceutical', 'shares': 833, 'price': 28.52}],
        "date": "20231109"
    }

portfolio_status9 = {
        "cash": 21.36,
        "stocks": [{'code': '600196.SH', 'name': 'Fosun Pharmaceutical', 'shares': 2239, 'price': 27.2}],
        "date": "20231211"
    }

portfolio_status10 = {
        "cash": 594.36,
        "stocks": [{'code': '600196.SH', 'name': 'Fosun Pharmaceutical', 'shares': 1739, 'price': 24.12},
                   {'code': '600519.SH', 'name': 'Kweichow Moutai', 'shares': 7, 'price': 1641}],
        "date": "20240109"
    }

portfolio_status11 = {
        "cash": 19.56,
        "stocks": [{'code': '600196.SH', 'name': 'Fosun Pharmaceutical', 'shares': 1763, 'price': 23.95},
                   {'code': '600519.SH', 'name': 'Kweichow Moutai', 'shares': 7, 'price': 1706}],
        "date": "20240208"
    }

portfolio_status12 = {
        "cash": 42847.6,
        "stocks": [{'code': '600519.SH', 'name': 'Kweichow Moutai', 'shares': 7, 'price': 1671.43}],
        "date": "20240311"
    }

# 回测每月投资组合并合并结果
portfolios = []
for portfolio_status in [portfolio_status1, portfolio_status2, portfolio_status3, portfolio_status4, portfolio_status5, portfolio_status6, portfolio_status7, portfolio_status8,portfolio_status9,portfolio_status10,portfolio_status11,portfolio_status12]:
    portfolio = backtest(portfolio_status)
    portfolios.append(portfolio)

# 合并所有月份的数据
combined_portfolio = pd.concat(portfolios)

# 获取大盘指数的模拟投资组合数据
start_date = min([portfolio_status1["date"], portfolio_status2["date"], portfolio_status3["date"], portfolio_status4["date"], portfolio_status5["date"], portfolio_status6["date"]])
end_date = (datetime.strptime(portfolio_status12["date"], "%Y%m%d") + relativedelta(months=1)).strftime("%Y%m%d")
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
