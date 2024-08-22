from datetime import datetime

from selenium import webdriver
import tushare as ts

from datetime import datetime,timedelta
ts.set_token("xx")
pro = ts.pro_api()
def convert_date_format(date_str):
    return datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d 00:00:00')

def get_news(end_date):
    
    
    # Convert start date format
    end_date_converted = convert_date_format(end_date)
    
    # Calculate end date (one day after start date)
    start_date_converted = (datetime.strptime(end_date, '%Y%m%d') - timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
    
    df = pro.news(src='sina', start_date=start_date_converted, end_date=end_date_converted)
    return df['content']

# # Example usage
# end_date = '20231121'
# content_titles = get_news(end_date)
# print(content_titles)


# def get_news(num=30):
#     browser = webdriver.Chrome()
#     browser.get('https://finance.sina.com.cn/7x24/')
#     html = browser.page_source
#     # parse html
#     from bs4 import BeautifulSoup
#     soup = BeautifulSoup(html, 'html.parser')
#     news = soup.find_all('p', class_="bd_i_txt_c", limit=num)
#     news_text = ""
#     for i in news:
#         news_text += i.text
#     # print today date and time in the format of YYYY/MM/DD hh:mm:ss
#     now = datetime.now()
#     # convert datetime to string
#     now = now.strftime("%Y/%m/%d %H:%M:%S")
#     return "**Today is " + now + "**\nHere is the news from sina finance: \n" + news_text


# if __name__ == "__main__":
#     start_date = '20231121'
#     end_date = '20231122'
#     print(get_new(start_date,end_date))
