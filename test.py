import pandas as pd
import math
from datetime import datetime,date
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import dash_auth
import dash_bootstrap_components as dbc

# 欄位修改:'日期':'date','損益':'pnl',日期改西元年datetime格式，stock_id換成股票代碼加中文名稱
def process_data(path='./data/GainLoss_Realized_2025.csv'):
    df = pd.read_csv(path)
    df = pd.read_csv(path, skiprows=1).iloc[:-1] # 從第2行開始讀取 刪除最後1行
    df = df.rename(columns={'Closed Date': 'date', 'Total Gain/Loss ($)': 'pnl'})
    df = df[df['date'] != 'Total']
    df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y') # 轉換日期格式
    df['pnl'] = df['pnl'].str.replace('$', '')  # 去除$符號
    df['pnl'] = df['pnl'].str.replace(',', '')  # 去除逗號
    df['pnl'] = df['pnl'].astype(float) # 轉換為浮點數
    df.drop(["Proceeds","Cost Basis (CB)","Total Gain/Loss (%)","Long Term (LT) Gain/Loss ($)","Long Term (LT) Gain/Loss (%)","Short Term (ST) Gain/Loss ($)","Short Term (ST) Gain/Loss (%)","Wash Sale?","Disallowed Loss","Transaction Closed Date","Transaction Cost Basis","Total Transaction Gain/Loss ($)","Total Transaction Gain/Loss (%)","LT Transaction Gain/Loss ($)","LT Transaction Gain/Loss (%)","ST Transaction Gain/Loss ($)","ST Transaction Gain/Loss (%)"], axis=1,inplace=True)  # 刪除欄位
    df['stock_id'] = df['Symbol']
    return df


class RealizedProfitLoss:
    def __init__(self,df):
        self.dataframe=df

    def plot(self,start_date=None, end_date=None):
        # 日期控制
        df=self.dataframe
        if start_date:
            df = df[df['date'] >= start_date]
        if end_date:
            df = df[df['date'] <= end_date]

        # 依照stock_id 分group計算每個標的的損益
        date_group = df.groupby(['date'])[['pnl']].sum()
        df = df.groupby(['stock_id'])[['pnl']].sum()
        df = df.reset_index()
        df = df.sort_values(['pnl'])
        # 分類賺賠
        df['category'] = ['profit' if i > 0 else 'loss' for i in df['pnl'].values]
        df['pnl_absolute_value'] = abs(df['pnl'])
        
        # 製作Sunburst賺賠合併太陽圖所需資料
        df_category = df.groupby(['category'])[['pnl_absolute_value']].sum()
        df_category = df_category.reset_index()
        df_category = df_category.rename(columns={'category': 'stock_id'})
        df_category['category'] = 'total'

        df_total = pd.DataFrame(
            {'stock_id': 'total', 'pnl_absolute_value': df['pnl_absolute_value'].sum(), 'category': ''},
            index=[0])
        df_all = pd.concat([df, df_category, df_total])

        labels = df['stock_id']

        # Create subplots: use 'domain' type for Pie subplot
        fig = make_subplots(rows=4,
                            cols=3,
                            specs=[[{'type': 'domain', "rowspan": 2}, {'type': 'domain', "rowspan": 2},{'type': 'domain', "rowspan": 2}],
                                   [None, None, None],
                                   [{'type': 'xy', "colspan": 3, "secondary_y": True}, None, None],
                                   [{'type': 'xy', "colspan": 3}, None, None]],
                            horizontal_spacing=0.03,
                            vertical_spacing=0.08,
                            subplot_titles=('Profit Pie: ' + str(df[df['pnl'] > 0]['pnl'].sum()),
                                            'Loss Pie: ' + str(df[df['pnl'] < 0]['pnl'].sum()),
                                            'Profit Loss Sunburst: '+str(df['pnl'].sum()),
                                            'Profit Loss Bar By Date',
                                            'Profit Loss Bar By Target',
                                            )
                            )
        # 獲利donut圖
        fig.add_trace(go.Pie(labels=labels, values=df['pnl'], name="profit", hole=.3, textposition='inside',
                            textinfo='percent+label'), row=1, col=1)
        # 虧損donut圖
        fig.add_trace(go.Pie(labels=labels, values=df[df['pnl'] < 0]['pnl'] * -1, name="loss", hole=.3,
                            textposition='inside', textinfo='percent+label'), row=1, col=2)
        # 賺賠合併太陽圖
        fig.add_trace(go.Sunburst(
            labels=df_all.stock_id,
            parents=df_all.category,
            values=df_all.pnl_absolute_value,
            branchvalues='total',
            marker=dict(
                colors=df_all.pnl_absolute_value.apply(lambda s: math.log(s + 0.1)),
                colorscale='earth'),
            textinfo='label+percent entry',
        ), row=1, col=3)

        # 每日已實現損益變化
        fig.add_trace(go.Bar(x=date_group.index, y=date_group['pnl'], name="date", marker_color="#636EFA"), row=3, col=1)
        fig.add_trace(
            go.Scatter(x=date_group.index, y=date_group['pnl'].cumsum(), name="cumsum_realized_pnl",
                      marker_color="#FFA15A"),
            secondary_y=True,row=3, col=1)
        
        # 標的損益變化
        fig.add_trace(go.Bar(x=df['stock_id'], y=df['pnl'], name="stock_id", marker_color="#636EFA"), row=4, col=1)
        
        # 修正Y軸標籤
        fig['layout']['yaxis']['title'] = '$USD'
        fig['layout']['yaxis2']['showgrid']=False
        fig['layout']['yaxis2']['title'] = '$USD(cumsum)'
        fig['layout']['yaxis3']['title'] = '$USD'
        
        # 主圖格式設定標題，長寬
        fig.update_layout(
            title={
                'text': f"Realized Profit Loss Statistic ({start_date}~{end_date})",
                'x': 0.49,
                'y': 0.99,
                'xanchor': 'center',
                'yanchor': 'top'},
            width=1200,
            height=1000)
        return fig
       
    def run_dash(self):
        # 取得今天日期並格式化
        today = date.today().strftime('%Y/%m/%d')

        # Build App 使用CSS樣式
        app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])  

        app.layout = html.Div(
            className='page',
            children=[
                html.Div(
                    [
                        html.Div(html.H1("Realized Profit Loss Dash")),
                        dbc.Row([dbc.Col(html.Div('今天日期')), dbc.Col(html.Div(f'{today}'))]),
                        dbc.Row([dbc.Col(html.Div('帳戶價值')), dbc.Col(html.Div('0'))]),
                        dbc.Row([dbc.Col(html.Div('部   位')), dbc.Col(html.Div('0'))]),
                        dbc.Row([dbc.Col(html.Div('現   金')), dbc.Col(html.Div('0'))]),
                        dbc.Row([dbc.Col(html.Div('每日變化')), dbc.Col(html.Div('0'))]),
                        dbc.Row([dbc.Col(html.Div('未實現收益')), dbc.Col(html.Div('0'))]),
                        dbc.Row([dbc.Col(html.Div('實際收益')), dbc.Col(html.Div('0'))]),
                    ]
                ),
                html.Br(),
                html.H4(html.P("date_range:")),
                dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=date(2000, 1, 1),
                    max_date_allowed=date(2050, 12, 31),
                    initial_visible_month=date(2025, 1, 1),
                    start_date=date(2025, 1, 1),
                    end_date=date(2025, 12, 31)
                ),
                # 繪圖
                dcc.Graph(id="graph")
            ]
        )

        @app.callback(
            Output("graph", "figure"),
            [Input('my-date-picker-range', 'start_date'),
             Input('my-date-picker-range', 'end_date')])

        def update_output(start_date, end_date):
            return self.plot(start_date, end_date)
            

        # Run app and display result inline in the notebook
        app.run(debug = True)



df=process_data()
RealizedProfitLoss(df).run_dash()
# df=df.dataframe
# start_date=date(2025, 1, 1)
# end_date=date(2025, 12, 31)
# if start_date:
#     df = df[df['date'].dt.date >= start_date]
# if end_date:
#     df = df[df['date'].dt.date <= end_date]

