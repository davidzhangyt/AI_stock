# import tushare as ts


import tushare as ts
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
ts.set_token("xxx")
pro = ts.pro_api()

def get_data(ts_code, end_date):
    end_date_dt = datetime.strptime(end_date, "%Y%m%d")
    
    # 计算start_date，提前一个月
    start_date_dt = end_date_dt - relativedelta(months=10)
    start_date = start_date_dt.strftime("%Y%m%d")
    start_date1=end_date
    # print(start_date)
    # print(end_date)
    price = pro.query('daily', ts_code=ts_code, start_date=start_date1, end_date=end_date,fields='ts_code,trade_date,close')
    income_df = pro.income(ts_code=ts_code, start_date=start_date, end_date=end_date, fields='ts_code,ann_date,f_ann_date,end_date,report_type,revenue,operate_profit,total_profit,n_income_attr_p,compr_inc_attr_p,basic_eps,diluted_eps')
    balance_df = pro.balancesheet(ts_code=ts_code, start_date=start_date, end_date=end_date,fields="ts_code,total_cur_assets,total_nca,total_hldr_eqy_inc_min_int,total_liab,total_assets")
    cashflow_df = pro.cashflow(ts_code=ts_code, start_date=start_date, end_date=end_date, fields="ts_code,ann_date,n_cashflow_act,n_cashflow_inv_act,n_cash_flows_fnc_act")
    fina_indicator = pro.query('fina_indicator', ts_code=ts_code, start_date=start_date, end_date=end_date, fields="ts_code,end_date,eps,gross_margin,bps,roe,roa,tax_to_ebt,rd_exp")

    income_meta_data = ["股票代码", "公告日期","实际公告日期", "报告期", "报告类型","营业收入", "营业利润", "利润总额", "净利润", "归属于母公司(或股东)的综合收益总额", "基本每股收益", "稀释每股收益"]
    balance_meta_data = ["股票代码", "流动资产合计", "非流动资产合计", "股东权益合计", "负债合计", "资产总计"]
    cashflow_meta_data = ["股票代码", "公告日期", "经营活动产生的现金流量净额", "投资活动产生的现金流量净额", "筹资活动产生的现金流量净额"]
    fina_indicator_meta_data = ["股票代码", "公告日期", "基本每股收益", "毛利率", "每股净资产", "ROE", "ROA", "所得税/利润总额", "研发费用"]
    price_meta_data = ["股票代码", "交易日期", "收盘价"]

    income_result = [{key: value for key, value in zip(income_meta_data, row.values)} for index, row in income_df.iterrows()]
    balance_result = [{key: value for key, value in zip(balance_meta_data, row.values)} for index, row in balance_df.iterrows()]
    cashflow_result = [{key: value for key, value in zip(cashflow_meta_data, row.values)} for index, row in cashflow_df.iterrows()]
    fina_indicator_result = [{key: value for key, value in zip(fina_indicator_meta_data, row.values)} for index, row in fina_indicator.iterrows()]
    price_result = [{key: value for key, value in zip(price_meta_data, row.values)} for index, row in price.iterrows()]
    # print({
    #     "利润表": income_result,
    #     "资产负债表": balance_result,
    #     "现金流量表": cashflow_result,
    #     "股票价格": price_result
    # })
    return {
        "利润表": income_result,
        "资产负债表": balance_result,
        "现金流量表": cashflow_result,
        "财务指标数据": fina_indicator_result,
        "股票价格": price_result
    }

if __name__ == "__main__":
    ts_code = '000858.SZ'
    # start_date = '20230303'
    end_date = '20230403'
    report = get_data(ts_code, end_date)
    

# ts.set_token("xx")
# pro = ts.pro_api()


# def income(start_date):
#     df = pro.income(ts_code='600000.SH', start_date='20180101', end_date='20180730', fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,basic_eps,diluted_eps')
#     mata_data = ["TS代码", "公告日期", "营业收入", "营业利润", "利润总额", "净利润", "归属母公司所有者净利润",
#                  "基本每股收益", "稀释每股收益"]
#     r = ""
#     for _index, _row in df.iterrows():
#         # print(row.values)
#         r += ", ".join([f"{key}: {value}" for key, value in zip(mata_data, _row.values)]) + "\n"
#     return r

# def balance(_start_date):
#     df = pro.balancesheet_vip(period=_start_date,
#                           fields="ts_code,total_cur_assets,total_nca,total_hldr_eqy_inc_min_int,total_liab,total_assets")
#     mata_data = ["ts代码", "流动资产合计", "非流动资产合计", "股东权益合计", "负债合计", "资产总计"]
#     r = ""
#     for _index, _row in df.iterrows():
#         # print(row.values)
#         r += ", ".join([f"{key}: {value}" for key, value in zip(mata_data, _row.values)]) + "\n"
#     return r

# def cashflow(_start_date):
#     df = pro.cashflow_vip(period=_start_date,
#                       fields="ts_code,ann_date,n_cashflow_act,n_cashflow_inv_act,n_cash_flows_fnc_act")
#     mata_data = ["ts代码", "公告日期", "经营活动产生的现金流量净额", "投资活动产生的现金流量净额", "筹资活动产生的现金流量净额"]
#     r = ""
#     for _index, _row in df.iterrows():
#         # print(row.values)
#         r += ", ".join([f"{key}: {value}" for key, value in zip(mata_data, _row.values)]) + "\n"
#     return r

# def get_fina_indicator(_start_date):
#     pro = ts.pro_api()
#     q = pro.query('fina_indicator_vip', start_date=_start_date)
#     r = q.to_string()
#     return r


# def financial_report_all(_start_date):
#     r = ""
#     r += "#利润表\n" + income(_start_date)
#     r += "#资产负债表\n" + balance(_start_date)
#     r += "#现金流量标\n" + cashflow(_start_date)
#     # r += "#财务指标数据\n" + get_fina_indicator(_start_date)
#     return r

# if __name__ == "__main__":
#     print(financial_report_all("20231231"))
