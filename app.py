import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly
import psutil

class SystemInfo():

    _instances = {}

    def __init__(self):
        self.time_log = []     # Real Time
        self.cpu_log = []       
        self.memory_log = []
        self.load_log = []

    # Singleton
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    @classmethod
    def append_data(cls, class_data, input_data):
        class_data.append(input_data)

# System information
sysinfo =  SystemInfo()

# App
app = dash.Dash(__name__)

style = {'padding': '5px', 'fontSize': '16px'}

app.layout = html.Div(
    html.Div(
    [
        html.H2("System Monitoring",style= style),
        html.Div(id='live-update-text'),
        dcc.Graph(id='live-update-graph'),
        dcc.Interval(
            id='interval-component',
            interval =  1 * 1000,       # in milliseconds
            n_intervals = 0
        )
    ]
    )
)


# Update data
@app.callback(Output('live-update-text','children'),
            Input('interval-component', 'n_intervals'))
def update_metrics(n):
    current_time = datetime.datetime.now()
    current_hour, current_minute, current_second = current_time.hour, current_time.minute, current_time.second
    current_cpu_info = sysinfo.cpu_log[-1]
    current_memory_info = sysinfo.memory_log[-1]
    current_load_info = sysinfo.load_log[-1]
    return [
        html.Span(f'CPU(%): {current_cpu_info}', style = style),
        html.Span(f'Memory(%): {current_memory_info }', style = style),
        html.Span(f'Load : {current_load_info }', style = style),
    ]

# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
                Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    sysinfo.append_data(sysinfo.time_log, datetime.datetime.now())
    sysinfo.append_data(sysinfo.cpu_log, psutil.cpu_percent())
    sysinfo.append_data(sysinfo.memory_log, psutil.virtual_memory().percent)
    sysinfo.append_data(sysinfo.load_log, psutil.getloadavg()[0]  )

    # Create the graph with subplots
    fig = plotly.tools.make_subplots(rows=3, cols=1, vertical_spacing=0.2)

    fig['layout']['margin'] = {
        'l': 30, 'r': 10, 'b': 30, 't': 10
    }
    fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}
    
    # System CPU 
    fig.append_trace({
        'x': sysinfo.time_log,
        'y': sysinfo.cpu_log,
        'name': 'cpu',
        'mode': 'lines',
        'type': 'scatter',
    }, 1, 1)

    # System Memory
    fig.append_trace({
        'x': sysinfo.time_log,
        'y': sysinfo.memory_log,
        'name': 'memory',
        'mode': 'lines',
        'type': 'scatter',
    }, 2, 1)

    # System Load
    fig.append_trace({
        'x': sysinfo.time_log,
        'y': sysinfo.load_log,
        'name': 'Load',
        'mode': 'lines',
        'type': 'scatter',
    }, 3, 1)

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)