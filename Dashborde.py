import pandas as pd
import dash
import matplotlib.pyplot as plt
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Create the Dash app
app = dash.Dash(__name__)

# Read the SpaceX launch data into pandas dataframe
spacex_csv_file = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_geo.csv'
df = pd.read_csv(spacex_csv_file)

launch_sites = df['Launch Site'].unique()
options = [{'label': 'All', 'value': 'all'}] + [{'label': site, 'value': site} for site in launch_sites]

# Get the minimum and maximum payload values from the dataframe for the RangeSlider
min_payload = df['Payload Mass (kg)'].min()
max_payload = df['Payload Mass (kg)'].max()

# App layout
# Add a new scatter plot to the layout for visualizing success vs. payload
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard', 
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 26}),
    
    # Dropdown to select launch site
    html.Div([
        html.H2('Select Launch Site:', style={'margin-right': '2em'}),
        dcc.Dropdown(options=options, value='all', id='location')
    ], style={'padding': '10px'}),
    
    # RangeSlider to select payload mass
    html.Div([
        html.H2('Select Payload Mass Range (kg):', style={'margin-right': '2em'}),
        dcc.RangeSlider(
            id='payload-slider',
            min=0, max=10000, step=1000,
            marks={i: str(i) for i in range(0, 10001, 1000)},
            value=[min_payload, max_payload]
        )
    ], style={'padding': '10px'}),
    
    # Placeholder for the pie chart
    html.Div(dcc.Graph(id='success-pie-chart'), style={'padding': '10px'}),

    # Placeholder for the scatter plot
    html.Div(dcc.Graph(id='success-payload-scatter-chart'), style={'padding': '10px'})
])

# Callback function to update pie chart based on selected site and payload range
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='location', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_pie_chart(selected_site, payload_range):
    filtered_df = df[(df['Payload Mass (kg)'] >= payload_range[0]) & 
                     (df['Payload Mass (kg)'] <= payload_range[1])]
    
    if selected_site == 'all':
        # If all sites are selected, show overall success rate for the payload range
        fig = px.pie(filtered_df, 
                     names='Launch Site', 
                     values='class', 
                     title='Overall Success Rate for All Sites',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    else:
        # Filter the dataframe for the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        
        # Create a pie chart for the selected site
        fig = px.pie(success_counts, 
                     names='class', 
                     values='count', 
                     title=f'Success vs Failure for {selected_site} (Filtered by Payload)',
                     labels={'class': 'Outcome', 'count': 'Count'},
                     color='class',
                     color_discrete_map={0: 'red', 1: 'green'})
    return fig

# Callback function to update the scatter plot based on selected site and payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='location', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_plot(selected_site, payload_range):
    # Filter the dataframe based on the selected payload range
    filtered_df = df[(df['Payload Mass (kg)'] >= payload_range[0]) &
                     (df['Payload Mass (kg)'] <= payload_range[1])]
    print(f"Filtered DataFrame size: {filtered_df.shape}")  # Debug statement

    if selected_site == 'all':
        # Show scatter plot for all sites
        title = 'Payload vs. Outcome for All Sites'
    else:
        # Filter for the selected site
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        title = f'Payload vs. Outcome for {selected_site}'
    
    print(f"Scatter plot for site: {selected_site}, DataFrame size: {filtered_df.shape}")  # Debug statement

    # Plot only if there is data to show
    if filtered_df.empty:
        return {
            'data': [],
            'layout': go.Layout(
                title='No data available for the selected criteria',
                xaxis={'title': 'Payload Mass (kg)'},
                yaxis={'title': 'Launch Outcome'},
            )
        }
    
    fig = px.scatter(
        filtered_df, x='Payload Mass (kg)', y='class',
        color='Booster Version Category',
        title=title,
        labels={'class': 'Launch Outcome', 'Payload Mass (kg)': 'Payload Mass (kg)'},
        color_discrete_sequence=px.colors.qualitative.G10
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)