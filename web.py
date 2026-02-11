import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go

def Drawing(dfTW, dfUS, dfMAIN, dfDAWHO):

    app = dash.Dash(__name__)   # 初始化 Dash 應用
    server = app.server # 關鍵：為了讓 Render 部署，必須暴露 Flask server
    
    fig = go.Figure()

    rowEvenColor = 'lightgrey'
    rowOddColor = 'white'
    
    # 使用 add_trace 新增表格 Data_Main = MainData.loc[:,['Date', 'XIRR', 'Profit$', 'Stock$', 'Cash$', 'Stock$%', 'Amount$', 'TWD_Base']]
    fig.add_trace(go.Table(
        header = dict(values=list(dfMAIN.columns),
                    line_color='darkslategray',
                    fill_color='royalblue',
                    align=['left','center','right','right','right','right','center','right','right'],
                    font=dict(color='white', size=12),
                    height=40),
        cells = dict(values=[dfMAIN.iloc[:,num] for num in range(len(dfMAIN.columns))],
                    line_color='darkslategray',
                    fill_color = [[rowOddColor,rowEvenColor]*40],
                    align=['left','center','right','right','right','right','center','right','right'],
                    font_size=12,
                    height=30))
    )
    
    app.layout = html.Div([
        dcc.Graph(figure=fig)
    ])

    app.run(debug=True)
    #if __name__ == '__main__':
    #    app.run(debug=True)

