
import processdata
import util

# ================= 處理各CSV資料轉成PANDAS =================
# 台股
result_TW = processdata.TW('./data/交易_第一南京.csv', './data/犇亞.csv')
# 美股
result_US = processdata.CS('./data/Balances_20241231.CSV', './data/Balances.CSV', './data/交易_CS嘉信.csv', './data/Positions.csv')
# 總表 將台股、美股的新台幣金額加總顯示
MainData = processdata.SummaryTable(result_TW, result_US)
# 大戶
result_DAWHO = processdata.DAWHO('./data/交易_永豐大戶.csv', './data/DAWHO.csv')

# ================= 計算各指標值 =================
# 持股比例
print(f'持股比例 - 台股 {result_TW.iloc[-1]["Stock$%"]:.0%}')
print(f'持股比例 - 美股 {result_US.iloc[-1]["Stock%"]:.0%}')
print(f'持股比例 - 總計 {MainData.iloc[-1]["Stock$%"]:.0%}')
print(f'持股比例 - 大戶 {result_DAWHO.iloc[-1]["Stock$%"]:.0%}')

# 計算年化報酬率(XIRR)
util.XIRR(result_TW)
util.XIRR(result_US)
util.XIRR(MainData)
util.XIRR(result_DAWHO)
print(f'台股 {result_TW.iloc[-1]["XIRR"]:.0%}')
print(f'美股 {result_US.iloc[-1]["XIRR"]:.0%}')
print(f'總計 {MainData.iloc[-1]["XIRR"]:.0%}')
print(f'大戶 {result_DAWHO.iloc[-1]["XIRR"]:.0%}')

# 與巴菲特距離指標
Year, XIRR, BuffettA, BuffettB, Buffett, Performance = util.Buffett(result_TW)
BuffettPerformanceTW = ("巴菲特績效 50 年平均 20% = 1.2^50 = 9,100 \n" \
        f"您 {Year:.1f} 年平均 {XIRR:.0%} 與巴菲特距離 {int(Buffett):3d} (越小越好), {Performance} \n" \
        f"{Year:.1f} 年的時間差距A=1.2^(50-{Year:.1f})，A^0.5 = {BuffettA:.0f} \n" \
        f"{XIRR:.0%} 的報酬率差距B (1+{XIRR:.0%})^B=9100，B = {BuffettB:.0f}年 \n" \
        f"與巴菲特距離 {int(Buffett):3d} =100*({BuffettA:.0f}^0.5*{BuffettB:.0f})/3,701 \n" \
        "  其中3,701 = ((1.2^(50-8))^0.5*log(9100,1+12%)) 是以12%報酬率投資8年計算出來")
Year, XIRR, BuffettA, BuffettB, Buffett, Performance = util.Buffett(result_US)
BuffettPerformanceUS = ("巴菲特績效 50 年平均 20% = 1.2^50 = 9,100 \n" \
        f"您 {Year:.1f} 年平均 {XIRR:.0%} 與巴菲特距離 {int(Buffett):3d} (越小越好), {Performance} \n" \
        f"{Year:.1f} 年的時間差距A=1.2^(50-{Year:.1f})，A^0.5 = {BuffettA:.0f} \n" \
        f"{XIRR:.0%} 的報酬率差距B (1+{XIRR:.0%})^B=9100，B = {BuffettB:.0f}年 \n" \
        f"與巴菲特距離 {int(Buffett):3d} =100*({BuffettA:.0f}^0.5*{BuffettB:.0f})/3,701 \n" \
        "  其中3,701 = ((1.2^(50-8))^0.5*log(9100,1+12%)) 是以12%報酬率投資8年計算出來")
Year, XIRR, BuffettA, BuffettB, Buffett, Performance = util.Buffett(MainData)
BuffettPerformanceMAIN = ("巴菲特績效 50 年平均 20% = 1.2^50 = 9,100 \n" \
        f"您 {Year:.1f} 年平均 {XIRR:.0%} 與巴菲特距離 {int(Buffett):3d} (越小越好), {Performance} \n" \
        f"{Year:.1f} 年的時間差距A=1.2^(50-{Year:.1f})，A^0.5 = {BuffettA:.0f} \n" \
        f"{XIRR:.0%} 的報酬率差距B (1+{XIRR:.0%})^B=9100，B = {BuffettB:.0f}年 \n" \
        f"與巴菲特距離 {int(Buffett):3d} =100*({BuffettA:.0f}^0.5*{BuffettB:.0f})/3,701 \n" \
        "  其中3,701 = ((1.2^(50-8))^0.5*log(9100,1+12%)) 是以12%報酬率投資8年計算出來")
Year, XIRR, BuffettA, BuffettB, Buffett, Performance = util.Buffett(result_DAWHO)
BuffettPerformanceDAWHO = ("巴菲特績效 50 年平均 20% = 1.2^50 = 9,100 \n" \
        f"您 {Year:.1f} 年平均 {XIRR:.0%} 與巴菲特距離 {int(Buffett):3d} (越小越好), {Performance} \n" \
        f"{Year:.1f} 年的時間差距A=1.2^(50-{Year:.1f})，A^0.5 = {BuffettA:.0f} \n" \
        f"{XIRR:.0%} 的報酬率差距B (1+{XIRR:.0%})^B=9100，B = {BuffettB:.0f}年 \n" \
        f"與巴菲特距離 {int(Buffett):3d} =100*({BuffettA:.0f}^0.5*{BuffettB:.0f})/3,701 \n" \
        "  其中3,701 = ((1.2^(50-8))^0.5*log(9100,1+12%)) 是以12%報酬率投資8年計算出來")
print(f'台股 {BuffettPerformanceTW}')
print(f'美股 {BuffettPerformanceUS}')
print(f'總計 {BuffettPerformanceMAIN}')
print(f'大戶 {BuffettPerformanceDAWHO}')

# 複合年均增長率 (CAGR) 
CAGR_TW = util.CalCAGR(result_TW)
CAGR_US = util.CalCAGR(result_US)
CAGR_MAIN = util.CalCAGR(MainData)
CAGR_DAWHO = util.CalCAGR(result_DAWHO)
print(f'{CAGR_TW:.0%}')
print(f'{CAGR_US:.0%}')
print(f'{CAGR_MAIN:.0%}')
print(f'{CAGR_DAWHO:.0%}')


# ================= 整理表格欄位  ================= 
# 清理不必要的欄位
Data_Main = MainData.loc[:,['Date', 'XIRR', 'Profit$', 'Stock$', 'Cash$', 'Stock$%', 'Amount$', 'TWD_Base']]
Data_TW = result_TW.loc[:,['Date', 'XIRR', 'Profit$', 'Stock$', 'Cash$', 'Stock$%', 'Amount$', 'TWD_Base']]
Data_US = result_US.loc[:,['Date', 'XIRR', 'Profit$', 'Stock$', 'Cash$', 'Stock$%', 'Amount$', 'TWD_Base']]
Data_DAWHO = result_DAWHO.loc[:,['Date', 'XIRR', 'Profit$', 'Stock$', 'Cash$', 'Stock$%', 'Amount$', 'TWD_Base']]
# 年
YearMain = Data_Main.loc[Data_Main.groupby(MainData['Date'].dt.year)['Date'].idxmax()]
YearMain['Date'] = YearMain['Date'].dt.strftime('%Y')
YearTW = Data_TW.loc[Data_TW.groupby(Data_TW['Date'].dt.year)['Date'].idxmax()]
YearTW['Date'] = YearTW['Date'].dt.strftime('%Y')
YearUS = Data_US.loc[Data_US.groupby(Data_US['Date'].dt.year)['Date'].idxmax()]
YearUS['Date'] = YearUS['Date'].dt.strftime('%Y')
YearDAWHO = Data_DAWHO.loc[Data_DAWHO.groupby(Data_DAWHO['Date'].dt.year)['Date'].idxmax()]
YearDAWHO['Date'] = YearDAWHO['Date'].dt.strftime('%Y')
# 年度獲利計算
YearMain['Annual Profit'] = YearMain['Profit$'].diff()
YearTW['Annual Profit'] = YearTW['Profit$'].diff()
YearUS['Annual Profit'] = YearUS['Profit$'].diff()
YearDAWHO['Annual Profit'] = YearDAWHO['Profit$'].diff()
# 月
MonthMain = Data_Main.loc[MainData.groupby([Data_Main['Date'].dt.year, Data_Main['Date'].dt.month])['Date'].idxmax()]
MonthMain['Date'] = MonthMain['Date'].dt.strftime('%Y/%m')
MonthTW = Data_TW.loc[Data_TW.groupby([Data_TW['Date'].dt.year, Data_TW['Date'].dt.month])['Date'].idxmax()]
MonthTW['Date'] = MonthTW['Date'].dt.strftime('%Y/%m')
MonthUS = Data_US.loc[Data_US.groupby([Data_US['Date'].dt.year, Data_US['Date'].dt.month])['Date'].idxmax()]
MonthUS['Date'] = MonthUS['Date'].dt.strftime('%Y/%m/%d')
MonthDAWHO = Data_DAWHO.loc[Data_DAWHO.groupby([Data_DAWHO['Date'].dt.year, Data_DAWHO['Date'].dt.month])['Date'].idxmax()]
MonthDAWHO['Date'] = MonthDAWHO['Date'].dt.strftime('%Y/%m/%d')

Data_Main['Date'] = Data_Main['Date'].dt.strftime('%Y/%m/%d')
Data_TW['Date'] = Data_TW['Date'].dt.strftime('%Y/%m/%d')
Data_US['Date'] = Data_US['Date'].dt.strftime('%Y/%m/%d')
Data_DAWHO['Date'] = Data_DAWHO['Date'].dt.strftime('%Y/%m/%d')

# 百分比
YearTW[['XIRR', 'Stock$%']] = YearTW[['XIRR', 'Stock$%']].map(lambda x: f'{x*100:.0f}%')
YearUS[['XIRR', 'Stock$%']] = YearUS[['XIRR', 'Stock$%']].map(lambda x: f'{x*100:.0f}%')
YearMain[['XIRR', 'Stock$%']] = YearMain[['XIRR', 'Stock$%']].map(lambda x: f'{x*100:.0f}%')
YearDAWHO[['XIRR', 'Stock$%']] = YearDAWHO[['XIRR', 'Stock$%']].map(lambda x: f'{x*100:.0f}%')
# 金額三位一撇
YearTW[['Profit$', 'Stock$', 'Cash$', 'Amount$', 'TWD_Base']] = YearTW[['Profit$', 'Stock$', 'Cash$', 'Amount$', 'TWD_Base']].map(lambda x: f'{x:,.0f}')
YearUS[['Profit$', 'Stock$', 'Cash$', 'Amount$', 'TWD_Base']] = YearUS[['Profit$', 'Stock$', 'Cash$', 'Amount$', 'TWD_Base']].map(lambda x: f'{x:,.0f}')
YearMain[['Profit$', 'Stock$', 'Cash$', 'Amount$', 'TWD_Base']] = YearMain[['Profit$', 'Stock$', 'Cash$', 'Amount$', 'TWD_Base']].map(lambda x: f'{x:,.0f}')
YearDAWHO[['Profit$', 'Stock$', 'Cash$', 'Amount$', 'TWD_Base']] = YearDAWHO[['Profit$', 'Stock$', 'Cash$', 'Amount$', 'TWD_Base']].map(lambda x: f'{x:,.0f}')

import web
web.Drawing(YearTW, YearUS, YearMain, YearDAWHO)






# ================= 投資儀表板DASHBOARD =================
# 各自持有的部位、現金價值
# 美股CAGR
# 資金佔比圖(甜甜圈)
# 投資表現圖(橫條圖) 損益%
# 股票部位(折線圖) $

# 合計價值圖(折線圖)
# 台股、美股投資組合分佈(甜甜圈)
# 資產分佈(甜甜圈)

# 總資產$
# USD/TWD匯率
# 匯兌損益$




#import draw
#draw.Drawing(result_US)



# # matplotlib繪圖時顯示繁體中文
# # 下載台北思源黑體
# import matplotlib
# import matplotlib.font_manager as fm
# fm.fontManager.addfont('TaipeiSansTCBeta-Regular.ttf')
# matplotlib.rc('font', family='Taipei Sans TC Beta')


# # https://en.moonbooks.org/Articles/How-to-Create-a-Gauge-Chart-Using-Python-/
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
# import numpy as np

# # 儀表板圖
# def gauge_chart(value, title='', min_val=0, max_val=100):
#     # Clamp the input value
#     value = max(min_val, min(max_val, value))

#     # Convert value to angular position (0° = max, 180° = min)
#     def val_to_deg(v):
#         return 180.0 * (1.0 - (v - min_val) / (max_val - min_val))

#     fig, ax = plt.subplots(figsize=(6, 3))
#     ax.set_aspect('equal')

#     # Define geometry
#     outer_r = 1.0
#     thickness = 0.30
#     inner_r = outer_r - thickness

#     # Color zones
#     zones = [
#         (0, 50, '#E5E8E8'),  # light gray
#         (50, 80, '#C8D6E5'),  # pale blue-gray
#         (80, 100, '#A3C1AD')  # desaturated green
#     ]

#     # Draw each zone as a wedge
#     for a, b, color in zones:
#         theta1 = val_to_deg(b)
#         theta2 = val_to_deg(a)
#         wedge = patches.Wedge(center=(0, 0), r=outer_r,
#                               theta1=theta1, theta2=theta2,
#                               width=thickness,
#                               facecolor=color, edgecolor='white', linewidth=1)
#         ax.add_patch(wedge)

#     # Subtle border behind the arc
#     bg_wedge = patches.Wedge(center=(0, 0), r=outer_r + 0.01,
#                              theta1=0, theta2=180, width=thickness + 0.02,
#                              facecolor='none', edgecolor='#DDDDDD', linewidth=1)
#     ax.add_patch(bg_wedge)

#     # Draw the needle
#     angle_deg = val_to_deg(value)
#     angle_rad = np.deg2rad(angle_deg)
#     needle_len = inner_r + thickness * 0.9
#     nx, ny = needle_len * np.cos(angle_rad), needle_len * np.sin(angle_rad)
#     ax.plot([0, nx], [0, ny], lw=3.5, color='#4C78A8', zorder=5)
#     ax.scatter([0], [0], s=120, color='#2F4F4F', zorder=6)

#     # Threshold marker (at 90%)閾值標記
#     threshold = 90
#     th_deg = val_to_deg(threshold)
#     th_rad = np.deg2rad(th_deg)
#     t_outer, t_inner = outer_r + 0.01, outer_r - 0.02
#     tx1, ty1 = t_inner * np.cos(th_rad), t_inner * np.sin(th_rad)
#     tx2, ty2 = t_outer * np.cos(th_rad), t_outer * np.sin(th_rad)
#     ax.plot([tx1, tx2], [ty1, ty2], lw=3, color='#FF6F61', zorder=7, solid_capstyle='round')

#     # Labels and text
#     ax.text(0, -0.20, f'{value:.0f}%', ha='center', va='center',
#             fontsize=28, fontweight='bold', color='#2F4F4F')
#     ax.text(0, -0.36, title, ha='center', va='center',
#             fontsize=12, color='#2F4F4F')

#     # Tick labels (0, 50, 80, 100)
#     for tick in [min_val, (min_val + max_val) / 2, max_val*0.8, threshold, max_val]:
#         d = val_to_deg(tick)
#         r_tick = outer_r + 0.07
#         x, y = r_tick * np.cos(np.deg2rad(d)), r_tick * np.sin(np.deg2rad(d))
#         ax.text(x, y, f'{int(tick)}', ha='center', va='center', fontsize=10, color='#666666')

#     ax.set_xlim(-1.15, 1.15)
#     ax.set_ylim(-0.35, 1.15)
#     ax.axis('off')
#     plt.tight_layout()  # 自動調整圖形標籤
#     #plt.savefig(f'{title}.png', dpi=300)
#     plt.show()


# # ===== 持股比例 =====
# # 儀表板圖
# stake = result_US.tail(1)['Stock$%'].item() * 100
# title = '持股比例'
# gauge_chart(stake, title=title)
# #files.download(f'{title}.png')

# # 甜甜圈圖
# labels = ['Cash', 'Stock']
# sizes = [result_US.tail(1)['Cash$'].item(), result_US.tail(1)['Stock$'].item()]
# colors = ['#E5E8E8', '#FF6B6B']
# wedgeprops = {'width': 0.4, 'edgecolor': 'white', 'linewidth': 2}

# fig, ax = plt.subplots()
# #ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors, wedgeprops=wedgeprops)
# ax.pie(sizes, startangle=270, colors=colors, wedgeprops=wedgeprops)
# # 設定圓餅圖中心位置文字
# stake = result_US.tail(1)['Stock$%'].item() * 100
# center_x, center_y = 0, 0
# ax.text(center_x, center_y, f'{stake:0.1f}%', ha='center', va='center', fontsize=36, color='black')

# ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
# plt.title('Cash vs Stock')
# plt.show()