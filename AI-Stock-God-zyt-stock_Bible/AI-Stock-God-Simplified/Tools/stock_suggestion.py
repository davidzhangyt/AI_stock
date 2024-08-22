


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
    start_date_dt = end_date_dt - relativedelta(months=1)
    start_date1 = start_date_dt.strftime("%Y%m03")
    # print(start_date1)
    
    data = pro.query('daily', ts_code=ts_code, start_date=start_date1, end_date=end_date)
    
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
    image_path = r'C:\Users\zddydy\Desktop\KlineCharts\price_chart.png'
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    fig.savefig(image_path)
    plt.close(fig)
    api_key = os.getenv("OPENAI_API_KEY", "sk-xx")

    base_url = "xx" # 

    # Function to encode the image
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    # # Path to your image
    # image_path = r'C:\Users\zddydy\Desktop\KlineCharts\price_chart.png'

    # Getting the base64 string
    base64_image = encode_image(image_path)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    text_prompt='''读取该K线图，根据下面的炒股圣经分析一下这个股票，并在最后面综合评价其走势以及是否可以购买，必须态度坚决肯定，不要出现模棱两可的判断，更不要出现股市有风险这种言论。
    三军会师，看好后市
    所谓的“三军会师”就是5日，10日，30日（或20日）安调易懂平均线，从高位向下运动到低位后，抬头向上，而且会合在一起。三线走到一块，意味着下降行情的结束，新一轮上升行情的开始，此时买入，是难得的赚钱机会，5日、10日、30日三条易懂平均线在低位会合时，表明短中长线投资者的持股成本渐渐一致，除短线有微薄的利润外，中长线均无获利盘，上档抛压不重，股价容易上升，所以“三军会师”图线是信的过的买入信号，应趁回档之际，逢低介入。
    双管齐下，买入不怕
    “双管齐下”是由两条并列的长下影小实体的图线组成的图形，股价下跌到低位后，如果连续出现两天长下影、小实体、且下影线的最低点较为接近时，就成为“双管齐下”，表明股价已经进入了底部，或者离底部不远，中长线投资者可以开始建仓，短线也可以介入，后市获利一般较为可靠，“双管齐下”是下档承接有力的迹象，股价跌到某一低点后，就能迅速被多头唾弃，说明做多的力量强大，同时也表明，在这一价位，抛压不重，后市能轻松的脱离底部，形成上升趋势。
    白龙出水，短线可为
    这里是指MACD中的dif图形，从0轴以下由下向上突破0轴的走势，因dif线在电脑屏幕上为白色的曲线，形似翻江倒海的一条白龙，0轴一下为海，dif线由下向上突破0轴线，就是“白龙”跃出了水面，故为“白龙出水”改形态，也是相当可信的买入信号，其原理是，dif线在0轴以下运动时，多为股价处在调整期，不宜做多，当dif线向上突破0轴时，表明调整已经结束，转入了上升行情，后市会出现较大幅度的上升走势，该形态是短线投资者难得的一次进场机会，获利机会相当大。
    五阳上阵，股价弹升
    “五阳上阵”是指股价跌到低位后，连续出现的五条小阳线的走势形态，这五条阳线，像五位英雄战士，整装待发，以便攻城夺地，取代“空军”表明后市将是多方的天下。此时可随“五阳”一道，参加夺城战斗，分享未来的胜利成果，五条阳线在低位出现时，表明底部做多的力量较强，连续五天都是多方取得胜利，“空头”已经被打的无立身之地，后市股价就会上升。
    身抱多线，好景出现
    股价下跌到低位以后，某天出现一条较大的图线，将前面的多条小图线包容起来，成为“一抱多线”,是非常可信的见底信号，此时进场，风险较小。该形态见底额原理是：一条大图线从上至下将前面的多条小图线包容，表示多方在全力围剿空方，决心夺回被空方掠去的地盘，后市显然免不了一番激烈的争斗，但最终的胜利，将会属于多方。“一抱多线”有两种形态，一种是大阳线包容前面的多条小图线，另一种是形态是大阴线包容前面的多条小图线，两种形态，后市均看好。
    三棒撑地，行情见底
    “三棒撑地”，是指股价跌到低位后，出现三条并列的长下影的小实体图线，处于低位的“三棒撑地”形态出现后，后市多有一涨，据此操作，成功率很高。该形态的见底原理与“一针锥底”和“双管齐下”原理相似，主要是股价跌到某一地点后，受到多方的支持，股价被无形的手唾弃，但人们的心态不稳，股价稍有涨升，就涌出抛盘，迫使股价下跌，当跌到前次出现的低点附近时，又受到支撑，使股价再度拉起，在心理因素的影响下，股价三度下探，仅仅前两次的低点附近时，投资者在此借入，并有“事不过三”的经验，不再短线卖出，股价相对稳定，处在观望中的投资者，此时也看好了希望，消除了顾虑，先后杀入，终于推动了股价稳步上扬，因此这种形态更可靠。

    '''
    payload = {
        # "model": "gpt-4-vision-preview",
        "model": "gpt-4o-2024-05-13",
        "messages": [
        {
            "role": "user",
            "content": [
            {
                "type": "text",
                "text": text_prompt
            },
            {
                "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
            ]
        }
        ],
        "max_tokens": 1000
    }
    # print(payload)
    # print(headers)
    response = requests.post(f"{base_url}/chat/completions", headers=headers, json=payload)
    
    result = response.json()
    
    # Extract the message content
    try:
        message_content = result['choices'][0]['message']['content']
    except Exception:
        print(result)
    # print(message_content)
    return data,message_content

if __name__ == "__main__":
   print(get_price("002594.SZ","20240708"))
