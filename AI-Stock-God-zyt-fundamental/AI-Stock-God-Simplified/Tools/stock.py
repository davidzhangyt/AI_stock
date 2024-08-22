import tushare as ts
import matplotlib.pyplot as plt
import pandas as pd
import os
import mplfinance as mpf
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
ts.set_token('xxx')

def get_price(ts_code, start_date, end_date):
    pro = ts.pro_api()
    
    
    data = pro.query('daily', ts_code=ts_code, start_date=start_date, end_date=end_date)
    
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
    image_path = r'C:\Users\zddydy\Desktop\KlineCharts\600519.png'
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    fig.savefig(image_path)
    plt.close(fig)
    return data
if __name__ == "__main__":
    data = get_price("002594.SZ", "20230403", "20240603")
    print(data)
