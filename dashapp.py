from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask.ext.heroku import Heroku

import pandas as pd
from functools import reduce

import dash
from dash.dependencies import Input, Output#, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.figure_factory as fifa

import os


#app = dash.Dash()
server = Flask(__name__)
#server.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/english'
heroku = Heroku(server)
server.secret_key = os.environ.get('APP_SECRET_KEY', 'my-secret-key')
db = SQLAlchemy(server)
app = dash.Dash(__name__, server=server)



mycol = ["id","personnel", "starttime", "endtime", "client", "section", "patient", "country", "summary"] 


def getdata():
    #conn = sql.connect("database.db")
    #sqlstring = "SELECT * FROM report"
    #df = pd.read_sql(sqlstring,conn)
    rows = db.session.execute("SELECT * FROM report;").fetchall()
    db.session.close()
    df = pd.DataFrame(rows,columns=mycol)
    #print(type(df["endtime"][0]))

    #df["time_required"] = pd.to_datetime(df["endtime"]) - pd.to_datetime(df["starttime"])
    df["time_required"] = df["endtime"] - df["starttime"]
    df["time_required(m)"] = df["time_required"].astype('timedelta64[m]')
    df["month"] = df["starttime"].apply(lambda x:str(x)[:7])
    df = df[["personnel","month","time_required(m)"]]
    df['month'] = df['month'].apply(lambda x:int(x.replace('-','')))
    #df["month"] = pd.to_datetime(df["month"])
    ff = df.groupby(["month","personnel"]).sum()
    ff = ff.reset_index()
    res = []
    for month in ff["month"].unique():
        tmp = ff[ff["month"]==month]
        tmp = tmp.drop("month",1)
        tmp = tmp.set_index("personnel").T
        tmp["month"] = month
        res.append(tmp)
    global ffc
    ffc = reduce(lambda x,y: pd.concat([x,y]), res)
    ffc = ffc.set_index("month")
    ffc = ffc.fillna(0)
    ffc = ffc.sort_index()
    return ffc

#getdata()

'''
def generate_table(dataframe):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(len(dataframe))]
    )
'''


def serve_layout():
    getdata()
    return html.Div([
        dcc.Dropdown(
            id='select-person',
            options=[{'label': i, 'value': i} for i in ffc.columns],
            multi=True,
            value=ffc.columns
        ),
        #html.Div(
        #    id='table-container'
        #),
        dcc.Graph(
            id='graph-with-range',
            animate=False
        ),
        dcc.Graph(
            id='my-table'
        ),
        dcc.RangeSlider(
            id='month-range',
            marks={str(i): i for i in ffc.index},
            min=ffc.index.min(),
            max=ffc.index.max(),
            value=[ffc.index.min(), ffc.index.max()],
            step=None
        )#,
        #dcc.Interval(
        #    id='interval-component',
        #    interval=5*1000 # in milliseconds
        #)
    ])

app.layout = serve_layout


@app.callback(
    Output('graph-with-range',  'figure'),
    [Input('month-range', 'value'),
     Input('select-person', 'value')]#,
     #events=[Event('interval-component', 'interval')]
     )
def update_figure(range_value, person_value):
    getdata()
    print(range_value[0], range_value[1], person_value)
    ffcf = ffc[(ffc.index >= range_value[0])&(ffc.index <= range_value[1])]
    ffcf = ffcf[person_value]
    traces = []
    for m in ffcf.index:
        traces.append(go.Bar(
            x=ffcf.columns,
            y=ffcf.loc[m,:],
            name='{}'.format(m),
            opacity=0.7
        ))
    return {
        'data':  traces,
        'layout':  go.Layout(
            barmode='stack',
            xaxis={'title': 'Personnel'},
            yaxis={'title': 'Time Required (m)'},
            title='English Translation Support'

        )
    }



@app.callback(
    Output('my-table', 'figure'),
    [Input('month-range', 'value'),
     Input('select-person', 'value')])
def update_table(range_value, person_value):
     ffcf = ffc[(ffc.index >= range_value[0])&(ffc.index <= range_value[1])]
     ffcf = ffcf[person_value]
     return fifa.create_table(ffcf, index=True, index_title='Y/M')


'''
@app.callback(
    Output('table-container', 'children'),
    [Input('month-range', 'value'),
     Input('select-person', 'value')]#,
     #events=[Event('interval-component', 'interval')]
     )
def update_table(range_value, person_value):
    getdata()
    ffcf = ffc[(ffc.index >= range_value[0])&(ffc.index <= range_value[1])]
    ffcf = ffcf[person_value]
    ffcf = ffcf.reset_index()
    return generate_table(ffcf)
'''


'''
@app.callback(
    Output('month-range', 'value'),
    events=[Event('interval-component', 'interval')])
def update_range():
    getdata()
'''



'''
@app.callback(
    Output('content', 'children'),
    events=[Event('interval-component', 'interval')])
def update_all():
    getdata()
'''


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
    #app.run(debug=True, host='0.0.0.0')
