import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, Input, Output, State

# Folder with the processed data (works on the laptop and on Render)
data_folder = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')

# Load the three files saved at the end of the notebook
zip_year = pd.read_csv(os.path.join(data_folder, 'zip_year.csv'), dtype={'zip_code': str})
borough_month = pd.read_csv(os.path.join(data_folder, 'borough_month.csv'))
crash_points = pd.read_csv(os.path.join(data_folder, 'crash_points.csv'), dtype={'zip_code': str},
                           parse_dates=['crash_date'])

# Extra columns for the charts
crash_points['weekday'] = crash_points['crash_date'].dt.dayofweek
borough_month['date'] = pd.to_datetime(borough_month[['year', 'month']].assign(day=1))

# Centre of each ZIP (average location of its crashes), used for the map
zip_centres = crash_points.groupby('zip_code')[['latitude', 'longitude']].mean().reset_index()

# Options for the dropdowns
boroughs = sorted(zip_year['borough'].unique())
years = sorted(zip_year['year'].unique())
housing_measures = {'complaints': 'Housing complaints',
                    'heat_problems': 'Heat/hot water problems',
                    'emergency_problems': 'Emergency housing problems'}
crash_measures = {'crashes': 'Serious crashes',
                  'severe_injuries': 'Severe injuries',
                  'fatalities': 'Fatalities'}

# A summary box: an icon, a big number and a label (kind = colour of the box)
def make_kpi(label, value, icon, kind):
    return html.Div(className=f'kpi kpi-{kind}', children=[
        html.Span(icon, className='kpi-icon'),
        html.Div([html.H3(value), html.P(label)]),
    ])


# A white card with a small coloured tag above the chart
def chart_card(tag, graph_id, height, extra_class=''):
    return html.Div(className=f'card chart-card {extra_class}', children=[
        html.Span(tag, className='chart-tag'),
        dcc.Graph(id=graph_id, style={'height': height}, config={'displaylogo': False}),
    ])


# A key finding: a big number or word and a short sentence
def finding(big, text, kind):
    return html.Div(className=f'finding finding-{kind}', children=[html.H3(big), html.P(text)])


# Same look for every chart: white background and the page font
px.defaults.template = 'plotly_white'
chart_font = {'family': 'Poppins, Segoe UI, sans-serif', 'color': '#1f2937'}

# Each borough always has the same colour
borough_colours = {'BRONX': '#e4572e', 'BROOKLYN': '#f3a712', 'MANHATTAN': '#29335c',
                   'QUEENS': '#17bebb', 'STATEN ISLAND': '#a8c686'}

app = Dash(__name__, title='NYC Housing × Street Safety',
           external_stylesheets=['https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap'])
server = app.server   # needed by Render to run the website

app.layout = html.Div(children=[

    # Hero banner
    html.Div(className='hero', children=[
        html.Div(className='hero-inner', children=[
            html.Span("NYC Open Data · 2022–2025", className='hero-kicker'),
            html.H1(["Unsafe homes, ", html.Span("unsafe streets?", className='highlight')]),
            html.P("Do the New York neighbourhoods with the most housing complaints also have the most "
                   "serious traffic crashes? Pick a borough, a year and what to compare, then generate your own report."),
            html.Div(className='hero-chips', children=[
                html.Span("🏠 2.65M housing problems", className='chip'),
                html.Span("🚑 11,958 serious crashes", className='chip'),
                html.Span("📍 200+ ZIP codes", className='chip'),
                html.Span("🗽 5 boroughs", className='chip'),
            ]),
        ]),
    ]),

    html.Div(className='page', children=[

        # Filters, search and the central button
        html.Div(className='card controls', children=[
            html.H2("Build your report"),
            html.Div(className='filters', children=[
                html.Div([html.Label("🗽 Borough"),
                          dcc.Dropdown(id='borough-filter', options=boroughs, value=boroughs, multi=True)]),
                html.Div([html.Label("📅 Year"),
                          dcc.Dropdown(id='year-filter', options=years, value=years, multi=True)]),
                html.Div([html.Label("🏠 Housing measure"),
                          dcc.Dropdown(id='housing-filter', value='complaints', clearable=False,
                                       options=[{'label': v, 'value': k} for k, v in housing_measures.items()])]),
                html.Div([html.Label("🚑 Crash measure"),
                          dcc.Dropdown(id='crash-filter', value='crashes', clearable=False,
                                       options=[{'label': v, 'value': k} for k, v in crash_measures.items()])]),
            ]),
            html.Div(className='search-row', children=[
                dcc.Input(id='search-box', type='text', debounce=True,
                          placeholder='🔍 Or just type, e.g. "Bronx 2024 heat fatalities", then press Enter'),
                html.Button("Generate Report", id='generate-button', n_clicks=0, className='generate-button'),
            ]),
            html.Div(id='report-status', className='status'),
        ]),

        # Summary numbers
        html.Div(id='kpi-row', className='kpi-row'),

        # Charts
        html.Div(className='chart-grid', children=[
            chart_card("Cross-domain", 'scatter-chart', '430px'),
            chart_card("Map", 'map-chart', '430px'),
            chart_card("Over time", 'trend-chart', '380px', 'full-width'),
            chart_card("Hotspots", 'bar-chart', '430px'),
            chart_card("When", 'heatmap-chart', '430px'),
        ]),

        # Story
        html.Div(className='card story', children=[
            html.H2("📖 The story"),
            html.Div(className='findings', children=[
                finding("0.83", "Correlation between housing complaints and serious crashes across ZIP codes", 'red'),
                finding("❄️ vs ☀️", "Complaints peak in winter, serious crashes peak in summer", 'blue'),
                finding("Top 10", "The ten ZIP codes high on both are all in the Bronx and Brooklyn", 'yellow'),
            ]),
            html.H3("The question"),
            html.P("Housing conditions and street safety are usually studied separately. We asked whether the same "
                   "NYC neighbourhoods carry both burdens: many housing maintenance complaints and many serious crashes."),
            html.H3("The data"),
            html.P("2.65 million housing problems reported to HPD and 11,958 serious-injury crashes investigated by NYC DOT "
                   "(SIRTA), 2022–2025. After cleaning, both were counted per ZIP code and year, and per borough and month."),
            html.H3("What we found"),
            html.Ul([
                html.Li("ZIP codes with more housing complaints also tend to have more serious crashes "
                        "(Spearman correlation 0.83 across all ZIP codes)."),
                html.Li("The ZIP codes high on both cluster in the Bronx, central and east Brooklyn and Upper Manhattan."),
                html.Li("The two peak in opposite seasons: complaints in winter (heat and hot water), crashes in summer."),
                html.Li("Crashes peak at evening rush hour and on weekend nights; complaints are reported in weekday office hours."),
                html.Li("High-burden ZIP codes have more problems and more crashes, but not different types of problems "
                        "or more severe crashes."),
            ]),
            html.H3("The limits"),
            html.P("These are associations, not causes. Larger and denser ZIP codes have more residents, buildings and "
                   "traffic, which explains much of the link; population data was not available to adjust for it. "
                   "SIRTA covers only serious crashes, so counts per ZIP code are small, and 9.7% of crashes have no ZIP code."),
            html.H3("Why it matters for New Yorkers"),
            html.P("The same neighbourhoods often face unsafe homes and unsafe streets at once. Housing inspections "
                   "and street-safety programmes could use this overlap to prioritise the ZIP codes that need both."),
        ]),

        html.P(className='footer', children=[
            "Data: NYC Open Data, HPD Housing Maintenance Code Complaints and Problems (ygpa-z7cr) and "
            "NYC DOT Serious Injury Response, Tracking & Analysis Program (xeqp-qz8h)."
        ]),
    ]),
])


@app.callback(
    Output('borough-filter', 'value'),
    Output('year-filter', 'value'),
    Output('housing-filter', 'value'),
    Output('crash-filter', 'value'),
    Output('report-status', 'children'),
    Output('kpi-row', 'children'),
    Output('scatter-chart', 'figure'),
    Output('map-chart', 'figure'),
    Output('trend-chart', 'figure'),
    Output('bar-chart', 'figure'),
    Output('heatmap-chart', 'figure'),
    Input('generate-button', 'n_clicks'),
    Input('search-box', 'n_submit'),
    State('search-box', 'value'),
    State('borough-filter', 'value'),
    State('year-filter', 'value'),
    State('housing-filter', 'value'),
    State('crash-filter', 'value'),
)
def generate_report(n_clicks, n_submit, search_text, selected_boroughs, selected_years,
                    housing_measure, crash_measure):
    # Search mode: words in the search box set the filters automatically
    if search_text:
        text = search_text.lower()
        found_boroughs = [b for b in boroughs if b.lower() in text]
        found_years = [y for y in years if str(y) in text]
        if found_boroughs:
            selected_boroughs = found_boroughs
        if found_years:
            selected_years = found_years
        if 'heat' in text:
            housing_measure = 'heat_problems'
        elif 'emergenc' in text:
            housing_measure = 'emergency_problems'
        elif 'complaint' in text:
            housing_measure = 'complaints'
        if 'fatal' in text or 'death' in text:
            crash_measure = 'fatalities'
        elif 'severe' in text or 'injur' in text:
            crash_measure = 'severe_injuries'
        elif 'crash' in text:
            crash_measure = 'crashes'

    # An empty filter means "all"
    if not selected_boroughs:
        selected_boroughs = boroughs
    if not selected_years:
        selected_years = years

    status = (f"Report for {', '.join(selected_boroughs)} | years {', '.join(str(y) for y in selected_years)} | "
              f"{housing_measures[housing_measure]} vs {crash_measures[crash_measure]}")
    # Keep only the selected boroughs and years
    filtered = zip_year[zip_year['borough'].isin(selected_boroughs) & zip_year['year'].isin(selected_years)]

    # Totals per ZIP for the selected years
    zip_totals = filtered.groupby(['zip_code', 'borough'])[[housing_measure, crash_measure]].sum().reset_index()

    # Summary numbers
    correlation = zip_totals[housing_measure].corr(zip_totals[crash_measure], method='spearman')
    kpis = [
        make_kpi(housing_measures[housing_measure], f"{filtered[housing_measure].sum():,}", "🏠", 'red'),
        make_kpi(crash_measures[crash_measure], f"{filtered[crash_measure].sum():,}", "🚑", 'blue'),
        make_kpi("ZIP codes", f"{zip_totals['zip_code'].nunique()}", "📍", 'yellow'),
        make_kpi("Spearman correlation", f"{correlation:.2f}" if pd.notna(correlation) else "n/a", "🔗", 'dark'),
    ]

    # Chart 1 (cross-domain): housing measure vs crash measure per ZIP
    scatter = px.scatter(zip_totals, x=housing_measure, y=crash_measure, color='borough',
                         hover_name='zip_code', color_discrete_map=borough_colours,
                         labels={housing_measure: housing_measures[housing_measure],
                                 crash_measure: crash_measures[crash_measure], 'borough': 'Borough'},
                         title=f"{housing_measures[housing_measure]} vs {crash_measures[crash_measure]}<br><sup>One dot per ZIP code</sup>")

    scatter.update_traces(marker={'size': 9, 'opacity': 0.8, 'line': {'width': 0.5, 'color': 'white'}})

    housing_label = housing_measures[housing_measure]
    crash_label = crash_measures[crash_measure]

    # Chart 2 (cross-domain map): one bubble per ZIP, colour = housing measure, size = crash measure
    map_data = zip_totals.merge(zip_centres, on='zip_code')
    map_data['bubble_size'] = map_data[crash_measure] + 1   # +1 so ZIPs with 0 still show
    map_chart = px.scatter_map(map_data, lat='latitude', lon='longitude', color=housing_measure,
                               size='bubble_size', hover_name='zip_code',
                               hover_data={'borough': True, housing_measure: True, crash_measure: True,
                                           'bubble_size': False, 'latitude': False, 'longitude': False},
                               color_continuous_scale='Reds', size_max=25, zoom=8.8,
                               center={'lat': 40.71, 'lon': -73.94}, map_style='carto-positron',
                               labels={housing_measure: housing_label, crash_measure: crash_label},
                               title=f"Map by ZIP code<br><sup>Colour = {housing_label.lower()}, size = {crash_label.lower()}</sup>")

    map_chart.update_layout(margin={'l': 10, 'r': 10, 't': 70, 'b': 10})

    # Chart 3: monthly trend of both datasets (borough × month table)
    trend_housing = housing_measure if housing_measure in borough_month.columns else 'complaints'
    monthly = borough_month[borough_month['borough'].isin(selected_boroughs) &
                            borough_month['year'].isin(selected_years)]
    monthly = monthly.groupby('date')[[trend_housing, 'crashes']].sum().reset_index()
    trend_chart = make_subplots(specs=[[{'secondary_y': True}]])
    trend_chart.add_trace(go.Scatter(x=monthly['date'], y=monthly[trend_housing], mode='lines+markers',
                                     name=housing_measures[trend_housing], line={'color': 'indianred'}),
                          secondary_y=False)
    trend_chart.add_trace(go.Scatter(x=monthly['date'], y=monthly['crashes'], mode='lines+markers',
                                     name='Serious crashes', line={'color': 'steelblue'}),
                          secondary_y=True)
    trend_chart.update_layout(title="Monthly trend of housing problems and serious crashes", template='plotly_white')
    trend_chart.update_yaxes(title_text=housing_measures[trend_housing], secondary_y=False)
    trend_chart.update_yaxes(title_text='Serious crashes', secondary_y=True)

    # Chart 4: top 10 ZIPs that rank high on both measures
    zip_totals['combined_rank'] = zip_totals[housing_measure].rank(pct=True) + zip_totals[crash_measure].rank(pct=True)
    top_zips = zip_totals.sort_values('combined_rank', ascending=False).head(10)
    bar_chart = px.bar(top_zips, x=crash_measure, y='zip_code', color=housing_measure, orientation='h',
                       hover_data=['borough'], color_continuous_scale='Reds',
                       labels={crash_measure: crash_label, housing_measure: housing_label, 'zip_code': 'ZIP code'},
                       title=f"Top 10 ZIP codes high on both<br><sup>{housing_label} and {crash_label.lower()}</sup>")
    bar_chart.update_yaxes(type='category', categoryorder='total ascending')

    # Chart 5: when crashes happen (weekday × hour)
    points = crash_points[crash_points['borough'].isin(selected_boroughs) & crash_points['year'].isin(selected_years)]
    if crash_measure == 'crashes':
        heat_table = pd.crosstab(points['weekday'], points['crash_hour'])
    else:
        heat_table = pd.crosstab(points['weekday'], points['crash_hour'], values=points[crash_measure], aggfunc='sum').fillna(0)
    heat_table = heat_table.reindex(index=range(7), columns=range(24), fill_value=0)
    heatmap_chart = px.imshow(heat_table, color_continuous_scale='Blues', aspect='auto',
                              x=list(range(24)), y=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                              labels={'x': 'Hour of day', 'y': 'Weekday', 'color': crash_label},
                              title=f"When do they happen?<br><sup>{crash_label} by weekday and hour</sup>")

    # Same font for every chart
    for chart in [scatter, map_chart, trend_chart, bar_chart, heatmap_chart]:
        chart.update_layout(font=chart_font, title_font={'size': 17})

    return (selected_boroughs, selected_years, housing_measure, crash_measure, status, kpis,
            scatter, map_chart, trend_chart, bar_chart, heatmap_chart)


if __name__ == '__main__':
    app.run(debug=True)