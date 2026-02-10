import pandas as pd
import datetime as dt



# 總表
def SummaryTable(result_TW, result_US):
    # 日期 XIRR 總獲利 股票 現金 持股比例 股票+現金 本金
    MainData = pd.merge(result_TW, result_US, on='Date', how='outer', suffixes=('_TW', '_US'))
    # NaN填值
    MainData.ffill(inplace=True)        # ffill往前填充，bfill往後填充
    MainData.fillna(0, inplace=True)    # 補0
    # 先用 fillna(0) 將 NaN 替換成 0 方便加法
    MainData['Profit$'] = MainData['Profit$_TW'].fillna(0) + MainData['Profit$_US'].fillna(0)
    MainData['Stock$'] = MainData['Stock$_TW'].fillna(0) + MainData['Stock$_US'].fillna(0)
    MainData['Cash$'] = MainData['Cash$_TW'].fillna(0) + MainData['Cash$_US'].fillna(0)
    MainData['Amount$'] = MainData['Amount$_TW'].fillna(0) + MainData['Amount$_US'].fillna(0)
    MainData['TWD_Base'] = MainData['TWD_Base_TW'].fillna(0) + MainData['TWD_Base_US'].fillna(0)
    # 持股比例
    MainData['Stock$%'] = MainData['Stock$']/MainData['Amount$']

    return MainData

# 台股
def TW(cash, stock):
    dfCASH_TW = pd.read_csv(cash)
    dfSTOCK_TW = pd.read_csv(stock)

    dfSTOCK_TW['日期'] = pd.to_datetime(dfSTOCK_TW['日期']) # 轉換日期格式
    dfCASH_TW['日期'] = pd.to_datetime(dfCASH_TW['日期'])
    # 最小日期
    Start_Date = min(dfSTOCK_TW['日期'].min(),dfCASH_TW['日期'].min())
    # 最大日期
    End_Date = max(dfSTOCK_TW['日期'].max(),dfCASH_TW['日期'].max())
    date_range = pd.date_range(start=Start_Date, end=End_Date, freq='D').normalize()
    #====================================================================================
    # 整理[犇亞]
    dfSTOCK_TW['日期'] = pd.to_datetime(dfSTOCK_TW['日期']) # 轉換日期格式
    dfSTOCK_TW['犇亞'] = dfSTOCK_TW['犇亞'].str.replace(',', '').astype(float)  # 去除逗號 轉換為浮點數
    # 刪除欄位
    dfSTOCK_TW.drop(["已投資資本（自首筆交易以來）", "Delta（自首筆交易以來）"], axis=1,inplace=True)
    # 重命名欄位
    dfSTOCK_TW.rename(columns={'日期': 'Date', '犇亞': 'Stock'}, inplace=True)
    dfSTOCK_TW = dfSTOCK_TW.set_index('Date').reindex()

    #====================================================================================
    # 處理[第一南京]格式
    dfCASH_TW.drop(["證券","股數","每股","對銷賬戶","備註"], axis=1,inplace=True) # 刪除欄位
    dfCASH_TW['日期'] = pd.to_datetime(dfCASH_TW['日期']) # 轉換日期格式
    dfCASH_TW['日期'] = dfCASH_TW['日期'].dt.strftime('%Y-%m-%d') # 去除時分秒
    dfCASH_TW['日期'] = pd.to_datetime(dfCASH_TW['日期']) # 轉換日期格式 datetime64[ns]
    dfCASH_TW['金額'] = dfCASH_TW['金額'].str.replace(',', '').astype(float)  # 去除逗號 轉換為浮點數
    dfCASH_TW['結餘'] = dfCASH_TW['結餘'].str.replace(',', '').astype(float)  # 去除逗號 轉換為浮點數

    # ========成本金額
    # 過濾類型條件等於存款的資料
    dfCOST_TW = dfCASH_TW[dfCASH_TW['類型'].isin(['存款'])].copy()
    dfCOST_TW.rename(columns={'日期': 'Date', '金額': 'TWD$'}, inplace=True)  # 重命名欄位
    dfCOST_TW.drop(["類型","結餘"], axis=1,inplace=True)  # 刪除欄位

    # ========取款為淨值減少
    Withdraw_TW = dfCASH_TW[dfCASH_TW['類型'].isin(['取款'])].copy()
    Withdraw_TW.rename(columns={'日期': 'Date', '金額': 'Withdraw'}, inplace=True)
    Withdraw_TW['Withdraw'] = Withdraw_TW['Withdraw'].abs() # 改為正數
    Withdraw_TW.drop(["類型","結餘"], axis=1,inplace=True) # 刪除欄位

    # ========每日現金餘額
    dfCASH_TW.rename(columns={'日期': 'Date', '結餘': 'Cash'}, inplace=True)  # 重命名欄位
    dfCASH_TW.drop(["類型","金額"], axis=1,inplace=True) # 刪除欄位
    # 刪除重複日期
    dfCASH_TW = dfCASH_TW.groupby('Date').head(1)  # 取得每日第一筆
    # 補齊缺少的日期資料
    dfCASH_TW = dfCASH_TW.set_index('Date').reindex(date_range) # 將日期設為index 將date_range設為data的index，fill_value=0將空值用0填滿
    #dfCASH_TW = dfCASH_TW.reset_index() # 重設index(即把ds設回一般欄位)
    # NaN填值  ffill往前填充，bfill往後填充
    dfCASH_TW.ffill(inplace=True)

    #====================================================================================
    # 合併
    result_TW = dfSTOCK_TW.join(dfCASH_TW)
    result_TW.reset_index(inplace=True)
    result_TW.rename(columns={'index': 'Date'}, inplace=True)
    result_TW.sort_values(by='Date', inplace=True)
    result_TW.dropna(inplace=True) # 刪除空白資料
    # 合併取款資料
    result_TW = pd.merge(result_TW,Withdraw_TW, on='Date' ,how='left')
    result_TW.fillna(0, inplace=True)

    result_TW.reset_index(drop=True, inplace=True)

    #===計算金額=========================================================================
    # 總金額
    result_TW['Amount'] = result_TW['Cash'] + result_TW['Stock']
    result_TW['Amount'] = result_TW['Amount'].round()

    # 累算投資金額
    def sum_costs_before(date):
        filtered = dfCOST_TW[dfCOST_TW['Date'] < date]
        return pd.Series({
            'TWD_Base': filtered['TWD$'].sum()
        })
    result_sums = result_TW['Date'].apply(sum_costs_before)
    result_TW = pd.concat([result_TW, result_sums], axis=1)

    # 台幣金額
    result_TW['Amount$'] = result_TW['Amount']
    result_TW['Amount$'] = result_TW['Amount$'].round()
    result_TW['Withdraw$'] = result_TW['Withdraw']
    result_TW['Withdraw$'] = result_TW['Withdraw$'].round()
    result_TW['Cash$'] = result_TW['Cash']
    result_TW['Cash$'] = result_TW['Cash$'].round()
    result_TW['Stock$'] = result_TW['Stock']
    result_TW['Stock$'] = result_TW['Stock$'].round()
    # 損益
    result_TW['Profit$'] = result_TW['Amount$']-result_TW['TWD_Base']
    result_TW['Profit$'] = result_TW['Profit$'].round()
    # 損益％
    result_TW['Profit$%'] = result_TW['Profit$']/result_TW['Amount$']
    # 持股比例
    result_TW['Stock$%'] = result_TW['Stock$']/result_TW['Amount$']

    return result_TW

# 美股
def CS(old, new, cash, stock):
    dfOLD_US = pd.read_csv(old)
    dfNEW_US = pd.read_csv(new)
    dfCASH_US = pd.read_csv(cash)
    dfSTOCK_US = pd.read_csv(stock, skiprows=2).iloc[:-2] # 從第3行開始讀取 刪除最後2行

    dfOLD_US['Date'] = pd.to_datetime(dfOLD_US['Date']) # 轉換日期格式
    dfNEW_US['Date'] = pd.to_datetime(dfNEW_US['Date'])
    dfCASH_US['日期'] = pd.to_datetime(dfCASH_US['日期'])
    # 最小日期
    Start_Date = min(dfOLD_US['Date'].min(),dfNEW_US['Date'].min())
    Start_Date = min(Start_Date,dfCASH_US['日期'].min())
    # 最大日期
    End_Date = max(dfOLD_US['Date'].max(),dfNEW_US['Date'].max())
    End_Date = max(End_Date,dfCASH_US['日期'].max())
    End_Date = End_Date + dt.timedelta(days=1)
    date_range = pd.date_range(start=Start_Date, end=End_Date, freq='D').normalize()

    #====================================================================================
    # 合併新的每日結餘
    dfNEW_US['Date'] = pd.to_datetime(dfNEW_US['Date']) # 轉換日期格式
    dfNEW_US['Date'] = dfNEW_US['Date'].dt.strftime('%Y/%m/%d') # 去除時分秒
    dfNEW_US['Amount'] = dfNEW_US['Amount'].str.replace('$', '')  # 去除$符號
    dfNEW_US['Amount'] = dfNEW_US['Amount'].str.replace(',', '')  # 去除逗號
    dfNEW_US['Amount'] = dfNEW_US['Amount'].astype(float) # 轉換為浮點數

    dfNEWn = pd.concat([dfNEW_US, dfOLD_US], ignore_index=True)  # ignore_index=True可以忽略合併時舊的index，改採用自動生成的index
    dfNEWn['Date'] = pd.to_datetime(dfNEWn['Date']) # 轉換日期格式
    dfNEWn.sort_values(by='Date', inplace=True)
    dfNEWn.reset_index(drop=True, inplace=True)
    dfNEWn.drop_duplicates(subset=['Date'], keep='first', inplace=True) # 根據特定欄位移除重複資料

    #====================================================================================
    # 處理嘉信每日餘額 + USD/TWD匯率
    # 下載USD/TWD的歷史數據
    import yfinance as yf
    from datetime import datetime, timedelta
    stock_data = yf.download('TWD=X', start=Start_Date, end=End_Date,auto_adjust=True)
    stock_data.rename(columns={'Close': 'FX'}, inplace=True)
    stock_data['FX'] = stock_data['FX'].round(decimals=4) #四捨五入

    # 去除分級表頭
    cols = stock_data.columns.map(lambda x: ''.join('' if 'TWD=X' in i else i for i in x))
    stock_data.columns = cols
    adj_close = stock_data['FX'] # 提取收盤價

    dfNEWn.set_index('Date', inplace=True) # 將 'Date' 欄位設置為索引
    #result = pd.concat([dfNEWn, adj_close])
    dfDayAmout = dfNEWn.join(adj_close)
    dfDayAmout.ffill(inplace=True)
    dfNEWn.reset_index(inplace=True)

    #====================================================================================
    # 處理[嘉信]每日現金餘額
    dfCASH_US['日期'] = pd.to_datetime(dfCASH_US['日期']) # 轉換日期格式
    dfCASH_US['日期'] = dfCASH_US['日期'].dt.strftime('%Y-%m-%d') # 去除時分秒
    dfCASH_US['日期'] = pd.to_datetime(dfCASH_US['日期']) # 轉換日期格式 datetime64[ns]
    dfCASH_US['金額'] = dfCASH_US['金額'].str.replace(',', '').astype(float)  # 去除逗號 轉換為浮點數
    dfCASH_US['結餘'] = dfCASH_US['結餘'].str.replace(',', '').astype(float)  # 去除逗號 轉換為浮點數
    dfCASH_US.drop(["股票代號","證券","股數","每股","對銷賬戶","費用","稅款","備註"], axis=1,inplace=True)  # 刪除欄位

    # ========取款為淨值減少
    Withdraw_US = dfCASH_US[dfCASH_US['類型'].isin(['取款'])].copy()
    Withdraw_US.drop(["類型","結餘"], axis=1,inplace=True) # 刪除欄位
    Withdraw_US.rename(columns={'日期': 'Date', '金額': 'Withdraw'}, inplace=True)
    Withdraw_US['Withdraw'] = Withdraw_US['Withdraw'].abs() # 改為正數

    dfCASH_US.drop(["類型","金額"], axis=1,inplace=True)  # 刪除欄位
    dfCASH_US.rename(columns={'日期': 'Date', '結餘': 'Cash'}, inplace=True)  # 重命名欄位
    # 刪除重複日期
    dfCASH_US = dfCASH_US.groupby('Date').head(1)  # 取得每日第一筆
    # 補齊缺少的日期資料
    dfCASH_US = dfCASH_US.set_index('Date').reindex(date_range) # 將日期設為index 將date_range設為data的index，fill_value=0將空值用0填滿
    #dfCASH_US = dfCASH_US.reset_index() # 重設index(即把ds設回一般欄位)
    # NaN填值  ffill往前填充，bfill往後填充
    dfCASH_US.ffill(inplace=True)

    #====================================================================================
    # 證券清單
    dfSTOCK_US.drop(["Description","Last Div (Last Dividend)",'Security Type',"Unnamed: 12"], axis=1,inplace=True)  # 刪除欄位
    dfSTOCK_US.rename(columns={'Qty (Quantity)':'Qty','Mkt Val (Market Value)': 'Value', 'Cost/Share':'Share', 'Cost Basis':'Cost', 'Gain $ (Gain/Loss $)':'Gain',
                'Gain % (Gain/Loss %)':'Gain%', '% of Acct (% of Account)':'Acct%'}, inplace=True)  # 重命名欄位
    # 處理欄位內容格式
    mapping = {'=': '', '"': "", r'\$': '', ',': '', '%': ''}  # $在正則表達式中表示行尾，所以需要用\轉義。r'\$'告訴Pandas把$視為字面字符
    dfSTOCK_US.replace(mapping, regex=True, inplace=True)
    dfSTOCK_US['Qty'] = dfSTOCK_US['Qty'].astype(float)
    dfSTOCK_US['Value'] = dfSTOCK_US['Value'].astype(float)
    dfSTOCK_US['Share'] = dfSTOCK_US['Share'].astype(float)
    dfSTOCK_US['Cost'] = dfSTOCK_US['Cost'].astype(float)
    dfSTOCK_US['Gain'] = dfSTOCK_US['Gain'].astype(float)
    dfSTOCK_US['Gain%'] = dfSTOCK_US['Gain%'].astype(float)
    dfSTOCK_US['Gain%'] = dfSTOCK_US['Gain%'].apply(lambda x: x/100)
    dfSTOCK_US['Acct%'] = dfSTOCK_US['Acct%'].astype(float)
    dfSTOCK_US['Acct%'] = dfSTOCK_US['Acct%'].apply(lambda x: x/100)

    #====================================================================================
    # 合併
    #result_US=pd.concat([dfDayAmout, dfCASH_US], axis=1)
    result_US = dfDayAmout.join(dfCASH_US)
    result_US.reset_index(inplace=True)
    result_US.rename(columns={'index': 'Date'}, inplace=True)
    result_US.sort_values(by='Date', inplace=True)
    #result_US.dropna(inplace=True) # 刪除沒有匯率的資料(假日) -->改補滿
    # 合併取款資料
    result_US = pd.merge(result_US,Withdraw_US, on='Date' ,how='left')
    result_US.fillna(0, inplace=True)
    result_US.reset_index(drop=True, inplace=True)

    #===計算金額=========================================================================
    # 反推 股票金額
    result_US['Stock'] = result_US['Amount'] - result_US['Cash']
    #result_US['Stock'] = result_US['Stock'].round()

    # 成本金額     多補今天日期代表台銀的美元金額
    dfCOST = pd.DataFrame({'Date':['2014-07-21','2020-06-10','2022-03-29', dt.date.today()],
                'USD$':[26200.00,10085.00,11240.00, 11883.49],
                'TWD$':[797041,295331,317216, 349465]})
    dfCOST['Date'] = pd.to_datetime(dfCOST['Date'])
    result_US['Date'] = pd.to_datetime(result_US['Date'])

    # 累算投資金額
    def sum_costs_before(date):
        filtered = dfCOST[dfCOST['Date'] < date]
        return pd.Series({
            'USD_Base': filtered['USD$'].sum(),
            'TWD_Base': filtered['TWD$'].sum(),
            'FX_Base': filtered['TWD$'].sum()/filtered['USD$'].sum()
        })
    result_sums = result_US['Date'].apply(sum_costs_before)
    result_sums['FX_Base'] = result_sums['FX_Base'].round(4)
    result_US = pd.concat([result_US, result_sums], axis=1)

    # 台幣金額$
    result_US['Amount$'] = result_US['Amount']*result_US['FX']
    result_US['Amount$'] = result_US['Amount$'].round()
    result_US['Withdraw$'] = result_US['Withdraw']*result_US['FX']
    result_US['Withdraw$'] = result_US['Withdraw$'].round()
    result_US['Cash$'] = result_US['Cash']*result_US['FX']
    result_US['Cash$'] = result_US['Cash$'].round()
    result_US['Stock$'] = result_US['Stock']*result_US['FX']
    result_US['Stock$'] = result_US['Stock$'].round()
    # 損益
    result_US['Profit'] = result_US['Amount']-result_US['USD_Base']
    result_US['Profit'] = result_US['Profit'].round(2)
    result_US['Profit$'] = result_US['Amount$']-result_US['TWD_Base']
    result_US['Profit$'] = result_US['Profit$'].round()
    # 損益％
    result_US['Profit$%'] = result_US['Profit$']/result_US['Amount$']
    # 匯兌損益 目前台幣金額-美元金額*成本匯率
    result_US['FXProfit$'] = result_US['Amount$']-result_US['Amount']*result_US['FX_Base']
    result_US['FXProfit$'] = result_US['FXProfit$'].round()
    # 持股比例
    result_US['Stock%'] = result_US['Stock']/result_US['Amount']
    result_US['Stock$%'] = result_US['Stock$']/result_US['Amount$']

    return result_US

def DAWHO(cash, stock):
    dfCASH_DAWHO = pd.read_csv(cash)
    dfSTOCK_DAWHO = pd.read_csv(stock)

    dfSTOCK_DAWHO['日期'] = pd.to_datetime(dfSTOCK_DAWHO['日期']) # 轉換日期格式
    dfCASH_DAWHO['日期'] = pd.to_datetime(dfCASH_DAWHO['日期'])
    # 最小日期
    Start_Date = min(dfSTOCK_DAWHO['日期'].min(),dfCASH_DAWHO['日期'].min())
    # 最大日期
    End_Date = max(dfSTOCK_DAWHO['日期'].max(),dfCASH_DAWHO['日期'].max())
    date_range = pd.date_range(start=Start_Date, end=End_Date, freq='D').normalize()
    #====================================================================================
    # 整理[DAWHO]
    dfSTOCK_DAWHO['DAWHO'] = dfSTOCK_DAWHO['DAWHO'].str.replace(',', '').astype(float)  # 去除逗號 轉換為浮點數
    # 刪除欄位
    dfSTOCK_DAWHO.drop(["已投資資本（自首筆交易以來）", "Delta（自首筆交易以來）"], axis=1,inplace=True)
    # 重命名欄位
    dfSTOCK_DAWHO.rename(columns={'日期': 'Date', 'DAWHO': 'Stock'}, inplace=True)
    dfSTOCK_DAWHO = dfSTOCK_DAWHO.set_index('Date').reindex()

    #====================================================================================
    # 處理[永豐大戶]格式
    dfCASH_DAWHO['日期'] = pd.to_datetime(dfCASH_DAWHO['日期']) # 轉換日期格式
    dfCASH_DAWHO['日期'] = dfCASH_DAWHO['日期'].dt.strftime('%Y-%m-%d') # 去除時分秒
    dfCASH_DAWHO['日期'] = pd.to_datetime(dfCASH_DAWHO['日期']) # 轉換日期格式 datetime64[ns]
    dfCASH_DAWHO['金額'] = dfCASH_DAWHO['金額'].str.replace(',', '').astype(float)  # 去除逗號 轉換為浮點數
    dfCASH_DAWHO['結餘'] = dfCASH_DAWHO['結餘'].str.replace(',', '').astype(float)  # 去除逗號 轉換為浮點數
    dfCASH_DAWHO.drop(["證券","股數","每股","對銷賬戶","備註"], axis=1,inplace=True) # 刪除欄位

    # ========成本金額
    # 過濾類型條件等於存款的資料
    dfCOST_DAWHO = dfCASH_DAWHO[dfCASH_DAWHO['類型'].isin(['存款'])].copy()
    dfCOST_DAWHO.rename(columns={'日期': 'Date', '金額': 'TWD$'}, inplace=True)  # 重命名欄位
    dfCOST_DAWHO.drop(["類型","結餘"], axis=1,inplace=True) # 刪除欄位

    # ========取款為淨值減少
    Withdraw_DAWHO = dfCASH_DAWHO[dfCASH_DAWHO['類型'].isin(['取款'])].copy()
    Withdraw_DAWHO.rename(columns={'日期': 'Date', '金額': 'Withdraw'}, inplace=True)
    Withdraw_DAWHO['Withdraw'] = Withdraw_DAWHO['Withdraw'].abs() # 改為正數
    Withdraw_DAWHO.drop(["類型","結餘"], axis=1,inplace=True) # 刪除欄位

    # ========每日現金餘額
    dfCASH_DAWHO.rename(columns={'日期': 'Date', '結餘': 'Cash'}, inplace=True)  # 重命名欄位
    dfCASH_DAWHO.drop(["類型","金額"], axis=1,inplace=True)  # 刪除欄位
    # 刪除重複日期
    dfCASH_DAWHO = dfCASH_DAWHO.groupby('Date').head(1)  # 取得每日第一筆
    # 補齊缺少的日期資料
    dfCASH_DAWHO = dfCASH_DAWHO.set_index('Date').reindex(date_range) # 將日期設為index 將date_range設為data的index，fill_value=0將空值用0填滿
    #dfCASH_UP = dfCASH_UP.reset_index() # 重設index(即把ds設回一般欄位)
    # NaN填值  ffill往前填充，bfill往後填充, fillna替換值
    dfCASH_DAWHO.ffill(inplace=True)

    #====================================================================================
    # 合併現金、股票資料
    result_DAWHO = dfSTOCK_DAWHO.join(dfCASH_DAWHO)
    result_DAWHO.reset_index(inplace=True)
    result_DAWHO.rename(columns={'index': 'Date'}, inplace=True)
    result_DAWHO.sort_values(by='Date', inplace=True)
    result_DAWHO.dropna(inplace=True) # 刪除空白資料
    # 合併取款資料
    result_DAWHO = pd.merge(result_DAWHO,Withdraw_DAWHO, on='Date' ,how='left')
    result_DAWHO.fillna(0, inplace=True)

    result_DAWHO.reset_index(drop=True, inplace=True)

    #===計算金額=========================================================================
    # 總金額
    result_DAWHO['Amount'] = result_DAWHO['Cash'] + result_DAWHO['Stock']
    result_DAWHO['Amount'] = result_DAWHO['Amount'].round()

    # 累算投資金額
    def sum_costs_before(date):
        filtered = dfCOST_DAWHO[dfCOST_DAWHO['Date'] < date]
        return pd.Series({
            'TWD_Base': filtered['TWD$'].sum()
        })
    result_sums = result_DAWHO['Date'].apply(sum_costs_before)
    result_DAWHO = pd.concat([result_DAWHO, result_sums], axis=1)

    # 台幣金額
    result_DAWHO['Amount$'] = result_DAWHO['Amount']
    result_DAWHO['Amount$'] = result_DAWHO['Amount$'].round()
    result_DAWHO['Withdraw$'] = result_DAWHO['Withdraw']
    result_DAWHO['Withdraw$'] = result_DAWHO['Withdraw$'].round()
    result_DAWHO['Cash$'] = result_DAWHO['Cash']
    result_DAWHO['Cash$'] = result_DAWHO['Cash$'].round()
    result_DAWHO['Stock$'] = result_DAWHO['Stock']
    result_DAWHO['Stock$'] = result_DAWHO['Stock$'].round()
    # 損益
    result_DAWHO['Profit$'] = result_DAWHO['Amount$']-result_DAWHO['TWD_Base']
    result_DAWHO['Profit$'] = result_DAWHO['Profit$'].round()
    # 損益％
    result_DAWHO['Profit$%'] = result_DAWHO['Profit$']/result_DAWHO['Amount$']
    # 持股比例
    result_DAWHO['Stock$%'] = result_DAWHO['Stock$']/result_DAWHO['Amount$']

    return result_DAWHO