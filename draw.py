import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go

def Drawing():
    app = dash.Dash(__name__)   # 初始化 Dash 應用

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode = "number+delta+gauge",    # number數值+delta差異值+gauge速度表
        value = 120,                    # 值
        delta = {'reference': 100},     # 顯示實際值和參考值之間的差異
        gauge = {   # 自訂axis（儀表的範圍）、steps（儀表的分段）和threshold （儀表上標記的值）
            'axis': {'visible': True, 'range': [None, 150]},
            'steps': [
                {'range': [0, 100], 'color': "lightgray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        },
        title = {"text": "Value 1"},            # 標題
        #domain = {'x': [0, 0.5], 'y': [0, 1]}   # 此參數決定每個指標所佔據的繪圖區域，這有助於我們將指標並排定位放置。
        domain = {'row': 2, 'column': 0}
        ))
    fig.add_trace(go.Indicator(
        mode = 'gauge', # 儀表板
        value = 200,
        delta = {'reference': 160},
        gauge = {
            'axis': {'visible': False}},    # axis儀表板範圍
        domain = {'row': 0, 'column': 0}))

    fig.add_trace(go.Indicator(
        value = 120,
        gauge = {
            'shape': "bullet",
            'axis' : {'visible': False}},
        #domain = {'x': [0.05, 0.5], 'y': [0.15, 0.35]}
        domain = {'row': 1, 'column': 0}
        ))

    fig.add_trace(go.Indicator(
        mode = "number+delta",  # number數值+delta差異值
        value = 300,
        domain = {'row': 0, 'column': 1}))

    fig.add_trace(go.Indicator(
        mode = "delta",
        value = 40,
        domain = {'row': 1, 'column': 1}))

    # 增加表格
    fig.add_trace(go.Table(header=dict(values=['A Scores', 'B Scores']),
                 cells=dict(values=[[100, 90, 80, 90], [95, 85, 75, 95]]))
                     )

    fig.update_layout(
        font=dict(
            family="./font/TaipeiSansTCBeta-Regular.ttf"     # 更新全域字型為「微軟正黑體」
        ),
        grid = {'rows': 3, 'columns': 2, 'pattern': "independent"},
        template = {'data' : {'indicator': [{
            'title': {'text': "Speed"},
            'mode' : "number+delta+gauge",
            'delta' : {'reference': 90}}]
                            }})
    
    app.layout = html.Div([
        dcc.Graph(figure=fig)
    ])
    app.run(debug=True)
    #if __name__ == '__main__':
    #    app.run(debug=True)
 

Drawing()
