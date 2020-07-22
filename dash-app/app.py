import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
from dash.dependencies import Input, Output
import datetime
import requests
import lxml.html as lh
import datetime
import re


def get_month_table(state,location,month,year):
    if month > 9: #month as a string to use for the URL def
        month_str = str(month)
    else: 
        month_str = '0'+str(month)
    #This code (next 3 lines) is adapted from https://towardsdatascience.com/web-scraping-html-tables-with-python-c9baba21059
    url='https://www.usharbors.com/harbor/'+state+'/'+location+'/tides/?tide='+year+'-'+month_str+'#monthly-tide-chart'
    #Create a handle, page, to handle the contents of the website
    page = requests.get(url)
    #Store the contents of the website under doc
    doc = lh.fromstring(page.content)
    #Parse data that are stored between <tr>..</tr> of HTML
    tr_elements = doc.xpath('//tr')
    #save the raw html rows as "table"
    table = tr_elements
    return(table)

def find_first_row(table):
    for row in range(len(table)):
        if table[row][0].text_content() == '1':
            return(row)

def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def scrape_from_url(state,location):
    #Empty df to store the data:
    df = []

    for month in range(1,13):
        month_str_display = months[month-1]
        table = get_month_table(state,location,month,year) #get the data for this month

        #find the first row
        row = find_first_row(table)

        #while the first entry of the row is less than the number of days in the month
        while isInt(table[row][0].text_content()):
            row_data = ['']*number_of_columns
            for col in range(number_of_columns):
                row_data[col] = table[row][col].text_content()
            row_data.insert(0,month_str_display)
            df.append(row_data)
            row+=1
    #Clean data
    column_names = ['Month','Date','Day','high_1','height_hi_1','high_2','height_hi_2','low_1','height_low_1','low_2','height_low_2','sunrise','sunset']
    data = pd.DataFrame(df,columns=column_names)
    high1 = pd.melt(data,id_vars=['Month','Date','Day','height_hi_1'],value_vars=['high_1'],var_name='event', value_name='time')
    high2 = pd.melt(data,id_vars=['Month','Date','Day','height_hi_2'],value_vars=['high_2'],var_name='event', value_name='time')
    low1 = pd.melt(data,id_vars=['Month','Date','Day','height_low_1'],value_vars=['low_1'],var_name='event', value_name='time')
    low2 = pd.melt(data,id_vars=['Month','Date','Day','height_low_2'],value_vars=['low_2'],var_name='event', value_name='time')
    sunrise = pd.melt(data,id_vars=['Month','Date','Day'],value_vars=['sunrise'],var_name='event', value_name='time')
    sunset = pd.melt(data,id_vars=['Month','Date','Day'],value_vars=['sunset'],var_name='event', value_name='time')
    high1 = high1.rename(columns={"height_hi_1": "height"})
    high2 = high2.rename(columns={"height_hi_2": "height"})
    low1 = low1.rename(columns={"height_low_1": "height"})
    low2 = low2.rename(columns={"height_low_2": "height"})
    sunrise['height'] = np.nan
    sunset['height'] = np.nan
    data = (pd.concat([high1, high2, low1, low2, sunrise, sunset])
         .sort_index()
         .reset_index())
    data = data[data['time']!='']
    
    #Put into long data format
    for row in range(len(data)):
        event = data['event'].iloc[row]
        time = data['time'].iloc[row]
        if (event == 'high_1' or event == 'low_1' or event == 'sunrise'): #morning events
            if not re.search('PM',str(time)):
                time = time + ' AM'
            time = pd.to_datetime(time).strftime('%H:%M %p')
        if (event == 'high_2' or event == 'low_2' or event == 'sunset'): #evening events
            if not re.search('AM',str(time)):
                time = time + ' PM'
            time = pd.to_datetime(time).strftime('%H:%M %p')
        data['time'].iloc[row] = time
    data['full_date'] = data['Month']+'-'+data['Date']+'-'+year+' '+data['time']
    data['full_date'] = pd.to_datetime(data['full_date'], format='%B-%d-%Y %H:%M %p')
    data['week_num'] = np.nan
    for row in range(len(data)):
        data['week_num'].iloc[row] = data['full_date'].iloc[row].isocalendar()[1]
        if data['Day'].iloc[row] == 'Sun':
            data['week_num'].iloc[row] += 1
    data = data.sort_values(by='full_date', ascending=True)
    return data

now = datetime.datetime.now() # current time
marion = pd.read_csv('tide-chart-great-hill-ma-2020.csv')
sd = pd.read_csv('tide-chart-ocean-beach-outer-coast-ca-2020.csv')

default_location = 'marion'
months = ['January','February','March','April','May','June','July','August','September','October','November','December']
year = '2020'
state = 'massachusetts'
number_of_columns = 12

app = dash.Dash()
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
    "background-color": colors['background'],
}

sidebar = html.Div(children=[
    html.H2(
        children='Dashboard Filters',
        style={
            'textAlign': 'left'
        }
    ),
    html.H3(
        children='Tide location:',
        style={
            'color': 'black'
        }
    ),
    dcc.Dropdown( #drop-down will eventually include all of the locations
        id='location_select',
        options=[
            {'label': 'Great Hill, MA', 'value': 'marion', 'title': 'Great Hill, MA'},
            {'label': 'Westport Harbor, MA', 'value': 'westport', 'title':'Westport Harbor, MA'}
        ],
        value=default_location
    ),
    html.H3(
        children='Number of days to show:',
        style={
            'color': 'black'
        }
    ),
    dcc.Slider( #slider will be the number of days to view on the spline plot
        id='future_days',
        min=1,
        max=10,
        step=1,
        value=5,
        marks={
        1: '1',2: '2',3: '3',4: '4',5: '5',6: '6',7: '7',8: '8',9: '9',10: '10'
        },
    )
    ],
    style=SIDEBAR_STYLE
)

content = html.Div(style=CONTENT_STYLE, children=[
    html.H1(
        children='Tide Calendar Downloader',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    html.Div(id='current_location', style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    html.Div(children='Last refresh occurred: ' + str(now), style={
        'textAlign': 'center',
        'color': colors['text']
    }),
    dcc.Store(id='df'),
    dcc.Store(id='fig_data'),
    dcc.Graph(id='main-plot', animate=False)
])

app.layout = html.Div([
    dcc.Location(id="url"), sidebar, content
    ])

# Use the inputs to scrape new tide data and display the chart

# load the data- will eventually scrape the data here
@app.callback(Output('df', 'data'),
              [Input('location_select','value')])
def scrape_data(location_select):
    if (location_select=='westport'):
        df = scrape_from_url('massachusetts','westport-harbor-ma')
    else:
        df = pd.read_csv('marion.csv')
    df = df[df['event']!='sunset']
    df = df[df['event']!='sunrise']
    df['full_date'] = pd.to_datetime(df['full_date'], format='%Y-%m-%d %H:%M')
    df = df.sort_values(by='full_date', ascending=True)
    dfdict = df.to_dict('list')
    diction = {'data': dfdict}
    return diction

@app.callback(Output('current_location', 'children'),
              [Input('location_select','value')])
def update_current_location(location_select):
    if location_select is None:
        location_select = default_location
    return 'Current location: ' + str(location_select)

# use the scraped data to create a plot
@app.callback(Output('fig_data','data'),
              [Input('df','data')])
def create_intial_figure(df):
    df = df['data']
    df = pd.DataFrame.from_dict(df)
    #print(df)
    fig_data = {'data': [
            go.Scatter(x=df['full_date'], 
                            y=df['height'],
                            line_shape='spline',
                            hoverinfo='text',
                            hovertext=df['time'],
                            line= dict(
                                width=4
                            ))
        ],
        'layout': {
            'plot_bgcolor': colors['background'],
            'paper_bgcolor': colors['background'],
            'font': {
                'color': colors['text']
            },
            'autosize': True,
            'shapes': [dict(
                type= 'line',
                yref= 'paper', y0= min(df['height']), y1= max(df['height']),
                xref= 'x', x0= now, x1= now,
                line= dict(color='Red')
            )],
            'xaxis': {
                'gridcolor': 'gray'
            },
            'yaxis': {
                'gridcolor': 'gray'
            },
        },
    }
    return {'data':fig_data}

# update the axes when the slider for number of days is changed
@app.callback(Output('main-plot', 'figure'),
              [Input('fig_data', 'data'),
              Input('future_days','value')])
def update_x_range(fig_data,future_days):
    fig_data = fig_data['data']
    fig= go.Figure(fig_data)
    fig.update_layout(xaxis_range=[now - datetime.timedelta(hours=12),now + datetime.timedelta(days=future_days)])
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)

