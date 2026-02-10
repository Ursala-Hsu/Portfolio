
from decimal import Decimal, ROUND_HALF_UP
# 處理四捨五入
def round_v3(num, decimal):
    str_deci = 1
    for _ in range(decimal):
        str_deci = str_deci / 10
    str_deci = str(str_deci)
    result = Decimal(str(num)).quantize(Decimal(str_deci), rounding=ROUND_HALF_UP)
    result = float(result)
    return result


# 計算年化報酬率(XIRR)
#pip install pyxirr   # PyXIRR - 用 Rust 寫的金融函數集合
import numpy as np
import pyxirr
#pip install tqdm       # 進度條
from tqdm.auto import tqdm
from tqdm import trange
def XIRR(result):
    for i in tqdm(range(len(result)-1), desc=f'XIRR計算'):
        i += 1
        xirr = result.loc[0:i, ['Date','Cash$','TWD_Base','Stock$']]
        # 現金增額	本金增額	投入增額 = 現金增額 - 本金增額
        xirr['現金增額'] = xirr['Cash$'].diff()
        xirr['本金增額'] = xirr['TWD_Base'].diff()
        xirr.fillna({'現金增額':xirr['Cash$'], '本金增額':xirr['TWD_Base']}, inplace=True) # 第一行
        xirr['投入增額'] = xirr['現金增額'] - xirr['本金增額']
        xirr['投入增額'] = xirr['投入增額'].round()
        xirr.loc[i,'投入增額'] = xirr.loc[i,'投入增額'] + xirr.loc[i,'Stock$'] # 最後一筆 投入增額+股票
        #print(xirr)
        #print(pyxirr.xirr(xirr['Date'], xirr['投入增額']))
        result.loc[i,'XIRR'] = pyxirr.xirr(xirr['Date'], xirr['投入增額'])

    # 用0取代nan
    result.fillna(0, inplace=True)
    result['XIRR'] = result['XIRR'].round(4)
    #result

# 與巴菲特距離指標
import pandas as pd
import math
def Buffett(result):
    data_types = {'Year': float, 'XIRR': float, 'BuffettA': float, 'BuffettB': float, 'Buffett': float, 'Performance': str}
    Buffett_Perf = pd.DataFrame(columns=data_types.keys()).astype(data_types)

    Year = (result["Date"].max()-result["Date"].min()).days / 365
    XIRR = result.iloc[-1]["XIRR"]
    BuffettA = (1.2**(50-Year))**0.5
    BuffettB = math.log(9100, (1+XIRR))
    Buffett = 100 * (BuffettA * BuffettB) / 3701
    Performance = BuffettPerformance(XIRR, Buffett)

    return Year, XIRR, BuffettA, BuffettB, Buffett, Performance

# 與巴菲特距離評語
def BuffettPerformance(XIRR, Buffett):
    if XIRR < 0 or Buffett > 168:
      return "多複習講稿"
    elif Buffett <= 168 and Buffett > 100:
      return "加油"
    elif Buffett <= 100 and Buffett > 21:
      return "成績優秀"
    elif Buffett <= 21:
      return "媲美巴菲特 !"

# 複合年均增長率 (CAGR) 
def CAGR(start, end, years):
    # 起始值 (Start Value): 期初價值
    # 最終值 (End Value): 期末價值
    # 年數 (Number of Years): 期間的年數
    if years <= 0:
      return 0 # 避免除以零
    return (end / start) ** (1 / years) - 1

from datetime import date
def calculate_years(start_date, end_date):
    """計算兩個日期之間的完整年數 (精確到實歲)"""
    # 如果日期是字串，需使用 datetime.strptime(s, "%Y-%m-%d").date() 轉換
    # 1. 基本年份差
    years = end_date.year - start_date.year
    # 2. 判斷今天(end_date)是否還未過生日(start_date)，若是則減 1
    # 檢查條件：(結束月, 結束日) < (開始月, 開始日)
    if (end_date.month, end_date.day) < (start_date.month, start_date.day):
        years -= 1
    return years

def CalCAGR(result):
    start_value = result['TWD_Base'].iloc[0]  # 期初價值
    end_value = result['Amount$'].iloc[-1] # 期末價值
    years = calculate_years(result['Date'].iloc[0], result['Date'].iloc[-1])

    return CAGR(start_value, end_value, years)
