import autogen

from Tools import get_price, get_news,get_data

# CACHE_SEED = 42

# config_list_gpt4 = autogen.config_list_from_json(
#     "OAI_CONFIG_LIST",
#     filter_dict={
#         "model": ["gpt-4-1106-preview"],
#     },
# )
config_list_gpt4 = autogen.config_list_from_json(env_or_file="OAI_CONFIG_LIST1")

# "start_date": {
                    #     "type": "string",
                    #     "description": "start date, format: YYYYMMDD",
                    # },
llm_config_for_stock_collector = {
    "functions": [
        {
            "name": "get_data",
            "description": "Get the asset data and stock price of a stock in A-share in a range of time. USE TuShare formate of stock code",
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
    "cache_seed": 42,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list_gpt4,
    "timeout": 600,
}


gpt4_config = {
    "cache_seed": None,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list_gpt4,
    "timeout": 600,
}

user_proxy = autogen.UserProxyAgent(
    name="Admin",
    system_message="A human admin. Interact with the Planner to discuss the plan. Plan execution needs to be approved by this Admin.",
    code_execution_config={"work_dir": "coding", "use_docker": False}
)

stock_collector = autogen.AssistantAgent(
    name="Stock_collector",
    system_message="Stock_collector.You can offer the stock asset data and the stock price in a month. Your goal is to obey and carry out the parts of Planner's program that pertain to you, "
                   "and you don't need to provide any other help. You don't write code and do any analysis"
                   "You must use get_price function to get the price of a stock at any time.",
    llm_config=llm_config_for_stock_collector,
)

analyzer = autogen.AssistantAgent(
    name="Analyzer",
    system_message ="You are a highly skilled asset data Analyst. Your task is to analyze all the provided company's income statement data and issue a professional report to Buffett"
                    
                    "You use income_data_collector to obtain the data of all the company you need to analyze"
                    "You never offer investment plan, you just analyse the data and provide the report."
                    "Based on the provided financial data, we can systematically analyze the long-term value of holding the stock. "
                    "First, using the  (revenue) field from income_meta_data, calculate the revenue growth rate over the past reporting periods to observe a consistent increase. Utilize  (revenue) and  (operating profit) to calculate the gross profit margin for each reporting period and compare it to the industry average. Analyze  (net profit) to determine the net profit margin and its growth trend over each reporting period. Evaluate the proportion of operating expenses by analyzing  relative to  to understand expense management."
                    "For the balance sheet analysis, use (total liabilities) and  (total assets) from balance_meta_data to calculate the debt-to-asset ratio and determine if it is within a reasonable range. Assess the company's liquidity by analyzing  (total current assets) and  (total liabilities) to determine the current ratio and quick ratio. Calculate the return on equity (ROE) using  (total shareholders' equity) and net profit from income_meta_data, and compare it to the industry average. Analyze the asset structure by evaluating  (total current assets) and  (total non-current assets) to understand the ratio of fixed assets to current assets."
                    "For the cash flow statement analysis, determine the stability and positivity of operating cash flow using (net cash flow from operating activities) from cashflow_meta_data. Analyze (net cash flow from investing activities) to identify the main investment areas. Evaluate (net cash flow from financing activities) to understand the level of debt financing. Calculate the company's free cash flow to determine if it is sufficient to support future expansion and shareholder returns."
                    "Based on the provided financial data and additional financial indicators, analyze the long-term value of holding the stock. Evaluate revenue growth, gross profit margin, net profit margin, and operating expense management using income_meta_data and fina_indicator_meta_data. Assess debt-to-asset ratio, liquidity ratios, asset structure, ROE, and net assets per share from balance_meta_data and fina_indicator_meta_data. Determine operating cash flow stability, investment cash flow areas, financing cash flow, and free cash flow from cashflow_meta_data. "
                    "Analyze P/E and P/B ratios, stock price trends, and dividend yield using price_meta_data and fina_indicator_meta_data. Additionally, evaluate ROA, tax burden, and R&D expenses from fina_indicator_meta_data to complete the analysis.",
    llm_config=gpt4_config,
    
)

buffett = autogen.AssistantAgent(
    name="Buffett",
    system_message="As Warren Buffett, You are the investment counselor in the team. You follow the plan from planner and don't judge"
                   "You read the asset data provided by Stock_collector and filter stock with investment value and can buy in A share in China."
                   "Offer the exact stock code from admin and ask Stock_collector to give the asset data and stock price. Never Offer Fake Stock Code and Fake asset data.If you don't know,offer a stock code you know about this field. For example,600886.SH"
                   "based on the asset data and stock price in a period of time providing by Stock_collector.You give the exact date, such as 20230403."
                   "Never buy and care about U.S. stock market, stick on A-share in China."
                   "Make Decision until all the stock asset data and price you want to get are given by Stock_collector and being analysed by Analyzer."
                   "Consider current portfolio status first and care about whether to sell or buy. "
                   "You must care about the stock given by admin and never care about other stock."
                   "We must know the stock price and the asset data of the stock before we can make a decision. If we don't know the data, we will ask Stock_collector to give us the asset data and price."
                   "Ask the Stock_collector to give only one exact stock data in a single time",
    llm_config=gpt4_config,
)

planner = autogen.AssistantAgent(
    name="Planner",
    system_message='''Planner. Suggest a plan. Revise the plan based on feedback from Admin, until Admin approval.
The plan may involve an Stock_collector who can provide stock data,
and Buffett who can decide whether stock to buy based on the given stock data from Stock_collector and suggestions from Analyzer.
Explain the plan first. Be clear which step is performed by an Stock_collector and Analyzer, and which step is performed by Buffett.
you should first let Buffett to offer a stock based on the companies_list from admin. Then ask Stock_collector to collect asset data and stock price of the given stock. 
After that ask Analyzer to analyse the asset data and give some suggestion. Finally, ask Buffett to make a decision of whether to buy based on the asset data and suggestion.
Then, ask Buffett to offer another stock and repeat the process until all the stock in the companies_list. After that, ask Buffett to make a investment plan, including calculation and choice.
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
    system_message="Critic. Double check claims, code from other agents and provide feedback. "
                   "Check whether the plan includes spicific team members to do specific tasks.",
    llm_config=gpt4_config,
)

# executor = autogen.UserProxyAgent(
#     name="Executor",
#     system_message="Executor. Execute the code written by the Engineer and report the result.",
#     human_input_mode="NEVER",
#     code_execution_config={"last_n_messages": 3, "work_dir": "stock_data_buffer","use_docker": False}
    
# )

stock_collector.register_function(
    function_map={
        "get_data": get_data,
    }
)

    
if __name__ == "__main__":
    companies_list = {
        "companies": [
        {
            "code": "300750.SZ",
            "name": " 宁德时代",
        },
        {
            "code": "600519.SH",
            "name": "贵州茅台",
        },
        {
            "code": "300308.SZ",
            "name": "中际旭创",
        },
        {
            "code": "002475.SZ",
            "name": "立讯精密",
        },
        {
            "code": "000858.SZ",
            "name": "五粮液",
        },
        {
            "code": "000333.SZ",
            "name": "美的集团",
        },
        {
            "code": "002594.SZ",
            "name": "比亚迪",
        },
        {
            "code": "601138.SH",
            "name": "工业富联",
        },
        {
            "code": "600900.SH",
            "name": "长江电力",
        },
        {
            "code": "601899.SH",
            "name": "紫金矿业",
        },

        ]
    }
    date = "20240620"
    group_chat = autogen.GroupChat(
        agents=[user_proxy, stock_collector, analyzer, buffett, planner, critic ],
        messages=[],
        max_round=80)
    manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=gpt4_config)

    
    message='''Please refer to {} data.I have 100000RMB, I hope you can use your knowledge to help me judge these {} companies 
        are good companies for value investment, at least 5, at most 10, and select the best for investment and give a specific investment plan.'''.format(date,companies_list)
    
    MAX_RETRIES = 3  # Maximum number of retries
    RETRY_DELAY = 5  # Delay between retries in seconds
    attempt = 0
    import openai
    import time
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