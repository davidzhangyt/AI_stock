


import tushare as ts
import matplotlib.pyplot as plt
import pandas as pd
import mplfinance as mpf
import os
import base64
import requests
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta

ts.set_token('xx')
def image(image_path):
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string
def get_price(ts_code, end_date):
    pro = ts.pro_api()
    end_date_dt = datetime.strptime(end_date, "%Y%m%d")
    
    # 计算start_date，提前一个月
    start_date_dt = end_date_dt - relativedelta(months=14)
    start_date1 = start_date_dt.strftime("%Y%m%d")
    # print(start_date1)
    
    data = pro.query('daily', ts_code=ts_code, start_date=start_date1, end_date=end_date)
    # print(data)
    data['trade_date'] = pd.to_datetime(data['trade_date'])
    
    data.sort_values('trade_date', inplace=True)  # Ensure data is sorted by date
    
    # Calculate moving averages
    data['MA5'] = data['close'].rolling(window=5).mean()
    data['MA10'] = data['close'].rolling(window=10).mean()
    data['MA20'] = data['close'].rolling(window=20).mean()

    # Prepare the data for mplfinance
    data.set_index('trade_date', inplace=True)
    data = data[['open', 'high', 'low', 'close', 'vol', 'MA5', 'MA10', 'MA20']]
    data.rename(columns={'vol': 'volume'}, inplace=True)

    # Define the moving averages to be plotted
    mav = (5, 10, 20)

    # Define the style
    mc = mpf.make_marketcolors(up='r', down='g', volume='in')
    s = mpf.make_mpf_style(marketcolors=mc)

    # Plot the candlestick chart with volume and moving averages
    fig, axlist = mpf.plot(data, type='candle', volume=True, mav=mav, style=s, title=f'{ts_code} Price Chart', ylabel='Price', ylabel_lower='Volume', returnfig=True)

    # Save the figure
    image_path = r'C:\Users\zddydy\Desktop\KlineCharts\BYD1.png'
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    fig.savefig(image_path)
    plt.close(fig)
    return data
if __name__ == "__main__":
   print(get_price("601888.SH","20240607"))
