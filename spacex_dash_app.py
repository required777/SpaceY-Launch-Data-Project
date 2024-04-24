# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                dcc.Dropdown(id='site-dropdown',
                                             options=[
                                                 {'label': 'All Sites', 'value': 'ALL'},
                                                 {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                 {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                 {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                 {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                                             ],
                                             value='ALL',
                                             placeholder="Select a Launch Site",
                                             searchable=True
                                             ),
                                    html.Br(),
                                    html.Div(dcc.Graph(id='success-pie-chart')),
                                    html.Br(),
                                    html.P("Payload range (Kg):"),
                                    dcc.RangeSlider(id='payload-slider',
                                                    min=min_payload,
                                                    max=max_payload,
                                                    step=1000,
                                                    marks={i: str(i) for i in range(int(min_payload), int(max_payload)+1, 1000)},
                                                    value=[min_payload, max_payload]
                                                    ),
                                    html.Div(id='output-container-range-slider'),
                                    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
                                ])
# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        pie_chart_data = spacex_df.groupby('Launch Site')['class'].value_counts().unstack(fill_value=0)
        pie_chart_data['Total'] = pie_chart_data.sum(axis=1)
        fig = px.pie(names=pie_chart_data.index, values=pie_chart_data['Total'], title='Total Successful Launches by Site')
    else:
        filtered_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(filtered_data, names='class', title=f'Successful vs Failed Launches at {selected_site}')
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    if selected_site == 'ALL':
        filtered_data = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                                  (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        title = 'Correlation between Payload and Success for All Sites'
    else:
        filtered_data = spacex_df[(spacex_df['Launch Site'] == selected_site) &
                                  (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                                  (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        title = f'Correlation between Payload and Success at {selected_site}'
    
    fig = px.scatter(filtered_data, x='Payload Mass (kg)', y='class', color='Booster Version Category', 
                     title=title, 
                     labels={'Payload Mass (kg)': 'Payload Mass (kg)', 'class': 'Launch Outcome', 
                             'Booster Version Category': 'Booster Version Category'})
    fig.update_layout(yaxis=dict(tickvals=[0, 1], ticktext=['Failed', 'Success']))
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
    
