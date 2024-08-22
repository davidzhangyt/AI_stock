import autogen
import time
import openai


MAX_RETRIES = 3  # Maximum number of retries
RETRY_DELAY = 5  # Delay between retries in seconds
from Tools import get_price, get_news

CACHE_SEED = None


config_list_gpt4 = autogen.config_list_from_json(env_or_file="OAI_CONFIG_LIST1")

# "start_date": {
                    #     "type": "string",
                    #     "description": "start date, format: YYYYMMDD",
                    # },
llm_config_for_stock_data_collector = {
    "functions": [
        {
            "name": "get_price",
            "description": "Get the price of a stock in A-share in a range of time. USE TuShare formate of stock code",
            "parameters": {
                "type": "object",
                "properties": {
                    "ts_code": {
                        "type": "string",
                        "description": "the stock code in the formate of TuShare, i.e., 000001.SZ",
                    },
                    
                    "end_date": {
                        "type": "string",
                        "description": "end date, format: YYYYMMDD",
                    },
                },
                "required": ["ts_code", "end_date"],
            }
        },
    ],
    "cache_seed": CACHE_SEED,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list_gpt4,
    "timeout": 600,
}

llm_config_for_news_reporter = {
    "functions": [
        {
            "name": "get_news",
            "description": "get news about finance",
            "parameters": {
                "type": "object",
                "properties": {
                    "end_date": {
                        "type": "string",
                        "description": "end date, format: YYYYMMDD",
                    },
                },
                "required": ["end_date"],
            }
        }
    ],
    "cache_seed": CACHE_SEED,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list_gpt4,
    "timeout": 600,
}

gpt4_config = {
    "cache_seed": None,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list_gpt4,
    "timeout": 240,
}

user_proxy = autogen.UserProxyAgent(
    name="Admin",
    system_message="A human admin. Interact with the Planner to discuss the plan. Plan execution needs to be approved by this Admin.",
    code_execution_config={"work_dir": "coding", "use_docker": False}
)

stock_data_collector = autogen.AssistantAgent(
    name="Stock_data_collector",
    system_message="Stock_data_collector.You can offer the stock price in a month. Your goal is to obey and carry out the parts of Planner's program that pertain to you, "
                   "and you don't need to provide any other help. You don't write code"
                   "You must use get_price function to get the price of a stock at any time.",
    llm_config=llm_config_for_stock_data_collector,
)

news_reporter = autogen.AssistantAgent(
    name="News_reporter",
    system_message="You are a helpful News_reporter. Your roll is to offer news. Your goal is to obey and carry out the parts of "
                   "Planner's program that pertain to you or requested by WeidongGe."
                   "And you don't need to provide any other help and MUST NEVER judge the plan. You don't write code."
                   "You MUST offer news by using get_news FUNCTION."
                   "You MUST offer news by using get_news FUNCTION.",
    llm_config=llm_config_for_news_reporter,
)

Weidong_Ge = autogen.AssistantAgent(
    name="WeidongGe",
    system_message="As Weidong Ge, You are the investment counselor in the team. You follow the plan from planner and don't judge"
                   "You read the news provided by News_reporter and filter stock with investment value and can buy in A share in China."
                   "Offer the exact stock code and ask Stock_data_collector to give the price. Never Offer Fake Stock Code and Fake Price.If you don't know,offer a stock code you know about this field. For example,002594.SZ"
                   "Based on the stock price and the stock suggestion in a period of time provided by Stock_data_collector and do some summary about its price and whether it is positive and negative.If you get the negative suggestion, MUST do not buy the stock or only buy a portion of it, and sell it immediately if you already hold it. "
                   "Never buy and care about U.S. stock market and HK market, ALWAYS stick on A-share Chinese stocks in China."
                   "If there is a clear negative tendency in the suggestion of Stock_data_collector, please do not purchase the stock and sell the stock, as this is a basic rule that MUST be followed."
                   "If you want to buy new stocks, you must choose stocks in the corresponding field of news that look very positive and choose less than 2 stocks. For example, if there is a war, stocks related to military industry may rise, so you need to choose a military industry stock to buy."
                   "YOU MUST Make Decision until ALL the stock price you want to get are given by Stock_data_collector."
                   "Ask the Stock_data_collector to give only one exact stock price in a single time."
                   "You MUST ensure that your stock code is correct and do not provide incorrect codes. If you are not clear about this company code, do not consider it as a potential choice, prioritize the pursuit of accuracy over excellence, and do not consider foreign companies."
                   "Must consider current portfolio status first at any time. After that, you can choose some stocks to buy based on the news provided by News_reporter. "
                   "Sell the stock if the stock price is negative and the stock is in the current portfolio. "
                   "When calculating portfolio, we first divide by the estimated amount of money to buy, estimate how many shares to buy, then take down integer shares, and then multiply the number of shares by the stock price to obtain the position of this stock. For example, if we choose to take out 10000 yuan from cash to buy a stock with a stock price of 54.12 yuan, and 10000/54.12=184.77, we take 150 shares and calculate 54.12 * 150=8118 yuan, which means our position is 150 shares and we spend cash of 8118 yuan."
                   "When buying stocks, we set a 0.1%\ overall transaction fee. You must buy at least 100 shares per stock, and the number of shares should be an integer value of 100 or more."
                   "When you offer portfolio, please obey the format of Current portfolio status"
                   "Final portfolio status MUST not exceed 5 stocks."
                   "You attach great importance to fundamental research, which he believes is the foundation of company investment. He will conduct in-depth research on the company's financial situation, industry position, and future development prospects to determine whether a company is worth investing in. This emphasis on fundamentals is also reflected in his investment decisions, as he chooses companies with strong fundamentals and growth potential for investment."
                   "Your investment strategy also includes band operations that follow market trends. He tends not to participate in short-term bands that are opposite to the general trend, but to grasp the market's follow the trend principle, which is to invest when the market trend is clear, in order to reduce risk and increase the possibility of returns."
                   "You also emphasized the principle of hedging from multiple perspectives to reduce overall systemic risk. This means that he will consider multiple factors when investing, diversify his investment portfolio to diversify risks and protect his investments from market fluctuations."
                   ,
    llm_config=gpt4_config,
)

planner = autogen.AssistantAgent(
    name="Planner",
    system_message='''Planner. Suggest a plan. Revise the plan based on feedback from Admin, until Admin approval.
The plan may involve an News_reporter who can provide today's news,
and Weidong Ge who can decide which stock to buy based on the stock price and today's news.
Explain the plan first. Be clear which step is performed by an Stock_data_collector, and which step is performed by Weidong Ge.
you should first let News_reporter collect today's news. Then let Weidong Ge decide which stocks we currently hold based on the current investment portfolio status, news, and stock prices, as well as industry related stocks with potential upward trends and corresponding stock codes that we want to consider based on the news.
After that ask Stock_data_collector to collect the stock price of the stock that Weidong Ge wants to know and then Weidong Ge make a summary about this stock. Finally, ask Weidong Ge to make a investment plan.
You never offer any decision and must ask the exact one to complete the plan.
''',
    llm_config=gpt4_config,
)

# engineer = autogen.AssistantAgent(
#     name="Engineer",
#     system_message="Engineer. You are the engineer in the team. You write code to analyze data and do calculations. "
#                    "Give your code to the Executor to execute.",
#     llm_config=gpt4_config,
# )

critic = autogen.AssistantAgent(
    name="Critic",
    system_message="Critic. Double check claims from other agents and provide feedback. "
                   "Check whether the plan includes spicific team members to do specific tasks and whether they execute them."
                   "Check the plan for any errors and inconsistencies when Weidong Ge already got the news and did some decision of potential investment areas and related stocks, for example, whether the code of stock is right and the stock is in related field. ",
    llm_config=gpt4_config,
)

# executor = autogen.UserProxyAgent(
#     name="Executor",
#     system_message="Executor. Execute the code written by the Engineer and report the result.",
#     human_input_mode="NEVER",
#     code_execution_config={"last_n_messages": 3, "work_dir": "stock_data_buffer","use_docker": False}
    
# )

stock_data_collector.register_function(
    function_map={
        "get_price": get_price,
    }
)

news_reporter.register_function(
    function_map={
        "get_news": get_news,
    }
)

    
if __name__ == "__main__":
    portfolio_status = {
        "cash": 17175.56,
        "stocks": [ {"code": "000063.SZ", "name": "ZTE Corporation", "shares": 300, "price": 29.12},
        {"code": "002594.SZ", "name": "BYD", "shares": 100, "price": 261.71},
        {"code": "688981.SH", "name": "SMIC", "shares": 600, "price": 48.94},
        {"code": "002253.SZ", "name": "Kawada Zhisheng", "shares": 700, "price": 11.22},
        {"code": "600115.SH", "name": "China Eastern Airlines", "shares": 1500, "price": 3.9},
        {"code": "600276.SH", "name": "Jiangsu Hengrui Medicine", "shares": 100, "price": 41.27},
],
        "date": "20240718"
    }
    date = "20240718"
    group_chat = autogen.GroupChat(
        agents=[user_proxy, stock_data_collector, news_reporter, Weidong_Ge, planner, critic],
        messages=[],
        max_round=80
    )
    manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=gpt4_config)

    message = '''Current portfolio status: {}. The currency unit is RMB. Based on this and today's date {}, 
    please help me update my investment plan in A-share based on your knowledge. You should consider how to distribute the money into different stocks.
    Please give me the updated portfolio status eventually.'''.format(portfolio_status, date)

    attempt = 0
    success = False

    while attempt < MAX_RETRIES and not success:
        try:
            user_proxy.initiate_chat(manager, message=message)
            success = True
        except openai.BadRequestError as e:
            if "expected a string, got null" in str(e):
                attempt += 1
                print(f"Retrying due to BadRequestError: {e}. Attempt {attempt} of {MAX_RETRIES}.")
                time.sleep(RETRY_DELAY)
            else:
                raise  # Re-raise the exception if it's not the specific error we are handling
        except openai.InternalServerError as e:
            print(f"Retrying due to InternalServerError: {e}. Attempt {attempt + 1} of {MAX_RETRIES}.")
            attempt += 1
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f"Unexpected error: {e}. Aborting.")
            break

    if not success:
        print("Failed to initiate chat after multiple attempts.")

# if __name__ == "__main__":
#     portfolio_status={
#         "cash":0.55,
#         "stocks":[{'code': '600519.SH', 'quantity': 55, 'price': 1666.99},{'code': '000651.SH', 'quantity': 275, 'price': 34.09}],
#         "date":"20230706"
#     }
#     date="20230706"
#     group_chat = autogen.GroupChat(agents=[user_proxy, stock_data_collector, news_reporter, buffett, planner, critic ],
#                                    messages=[],
#                                    max_round=80)
#     manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=gpt4_config)
#     user_proxy.initiate_chat(
#         manager,
#         # message="Please refer to 20240327 data. I have 100000 RMB, I need you to help me make an investment plan in A-share based on your knowledge."
#         #         "You should consider how to distribute the money into different stocks."
#         #         "please give your final result in the form of table. Use TuShare formate code for stock."
#         message='''Current portfolio status: {}.The currency unit is RMB.Based on this and today's date {}, 
#         please help me update my investment plan in A-share based on your knowledge.You should consider how to distribute the money into different stocks.
#         Please give me the updated portfolio status eventually''' .format(portfolio_status, date)
#     )

    