import random
import plotly
import pandas as pd
from typing import List, Dict, Tuple, Any
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px

from data import get_data, count_words_in_title, get_word_counts, get_reading_time, get_average_readed_word
from data import get_added_time_series, get_archived_time_series
from data import get_language_counts, get_favorite_count, get_domain_counts
from constants import DEFAULT_READING_SPEED, ACCESS_TOKEN, MAX_NUMBER_OF_RECORDS, DASH_APP_INDEX_STRING


INPUT_SECTION_STYLE = {'width': '100%', 'font-size': '30px'}


def plot_two_columns(col0: Any, col1: Any, width0_percent: float = 50) -> html.Div:
    assert 0 <= width0_percent and width0_percent <= 100, width0_percent
    width1_percent = 100 - width0_percent
    return html.Div(className='row', children=[
        html.Div([col0], className='two-columns--0', style={'width': f'{width0_percent}%'}),
        html.Div([col1], className='two-columns--1', style={'width': f'{width1_percent}%'}),
    ])


def word_cloud_plot(data: List[Dict]) -> dcc.Graph:
    word_cnts = count_words_in_title(data)
    n_word = len(word_cnts)
    words = list(word_cnts.keys())
    weights = [word_cnts[w] for w in words]
    colors = [plotly.colors.DEFAULT_PLOTLY_COLORS[random.randrange(1, 10)] for i in range(n_word)]
    data = go.Scatter(x=[random.random() for i in range(n_word)],
                      y=[random.random() for i in range(n_word)],
                      mode='text',
                      text=words,
                      marker={'opacity': 0.3},
                      textfont={'size': weights,
                                'color': colors})
    layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}})
    fig = go.Figure(data=[data], layout=layout)
    return dcc.Graph(figure=fig)


def articles_over_time_plot(data: List[Dict], should_cumsum: bool = True) -> dcc.Graph:
    df = get_added_time_series(data)
    archived_df = get_archived_time_series(data)
    if len(archived_df) > 0:
        df = pd.merge(df, archived_df, how='outer', left_index=True, right_index=True)
    if should_cumsum:
        df.fillna(0, inplace=True)
        df = df.cumsum()
    fig = px.line(df,
                  labels={'index': 'Date', 'value': 'Number of articles'},
                  title='Article Count Over Time')
    return dcc.Graph(figure=fig)


def word_counts_plot(data: List[Dict]) -> dcc.Graph:
    n_last_day_options = [360, 90, 30, 7, 2]
    avg_readed_words = [int(get_average_readed_word(data, n_last_day)) for n_last_day in n_last_day_options]
    avg_readed_words_table = dash_table.DataTable(
        id='readed-words',
        columns=[{'name': f'{i} days', 'id': f'{i}_days'} for i in n_last_day_options],
        data=[{f'{i}_days': avg_readed_words[pos] for pos, i in enumerate(n_last_day_options)}],
    )
    # histogram
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=get_word_counts(data, filters=[['status', '=', 0]]),  # unread
        name='Unread articles',
    ))
    fig.add_trace(go.Histogram(
        x=get_word_counts(data, filters=[['status', '=', 1]]),  # archived
        name='Archived articles',
    ))
    fig.update_layout(
        title_text='Word Count Distribution',  # title of plot
        xaxis_title_text='Number of words',
        yaxis_title_text='Number of articles',
        barmode='stack'  # The two histograms are drawn on top of another
    )
    return html.Div([
        html.H3(children='Average readed words recently (words / day)', className='center-text'),
        avg_readed_words_table,
        dcc.Graph(figure=fig)
    ])


# -------------------- Reading time -------------------- #
def get_reading_time_chart(data: List[Dict], reading_speed: int) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=get_reading_time(data, reading_speed=reading_speed, filters=[['status', '=', 0]]),  # unread
        name='Unread articles',
    ))
    fig.add_trace(go.Histogram(
        x=get_reading_time(data, reading_speed=reading_speed, filters=[['status', '=', 1]]),  # archived
        name='Archived articles',
    ))
    fig.update_layout(
        title_text='Reading Time Distribution',  # title of plot
        xaxis_title_text=f'Estimated reading time (minutes) with reading speed = {reading_speed} wpm',
        yaxis_title_text='Number of articles',
        barmode='stack'  # The two histograms are drawn on top of another
    )
    return fig


def get_reading_time_needed(data: List[Dict], reading_speed: int, reading_minutes_daily: int) -> html.Div:
    total_minutes = int(sum(get_reading_time(data, reading_speed=reading_speed, filters=[['status', '=', 0]])))
    days = int(total_minutes / reading_minutes_daily)
    hours = int((total_minutes % reading_minutes_daily) / 60)
    minutes = total_minutes % 60
    ans = ''
    if days > 0:
        ans += f' {days} days'
    if hours > 0:
        ans += f' {hours} hours'
    if minutes > 0:
        ans += f' {minutes} minutes'
    title = f'Total reading time needed (with {reading_speed} words / minute and {reading_minutes_daily} minutes / day)'
    return html.Div([
        html.H3(children=title, className='center-text'),
        html.Div(children=ans, className='center-text highlight'),
    ])


def reading_time_plot(data: List[Dict]) -> html.Div:
    max_reading_speed = DEFAULT_READING_SPEED * 3
    max_reading_minutes_daily = 24 * 60
    return html.Div([
        html.H3(children='Reading speed (words / minute)', className='center-text'),
        dcc.Slider(
            id='reading-speed',
            marks={i: str(i) for i in range(100, max_reading_speed, 100)},
            min=1, max=max_reading_speed, step=10, value=DEFAULT_READING_SPEED
        ),
        html.H3(children='Reading time spent daily (minutes / day)', className='center-text'),
        dcc.Slider(
            id='reading-minutes-daily',
            marks={i: str(i) for i in range(120, max_reading_minutes_daily, 240)},
            min=10, max=max_reading_minutes_daily, step=10, value=60,
        ),
        html.Div(id='reading-time-needed', children=''),
        # figure will be updated by update_reading_time_components()
        dcc.Graph(id='reading-time-chart', figure=go.Figure()),
    ])


# -------------------- Domain -------------------- #
def domain_counts_plot(data: List[Dict], limit: int = 20) -> dcc.Graph:
    top_pairs = list(get_domain_counts(data).items())  # both unread + archived
    top_pairs.sort(key=lambda p: -p[1])  # sort desc by count
    top_pairs = top_pairs[:limit]  # display top items only
    top_pairs.reverse()  # because px.bar display the items in a reversed order
    top_domains = [p[0] for p in top_pairs]
    unread_domain_cnts = get_domain_counts(data, filters=[['status', '=', 0]])
    archived_domain_cnts = get_domain_counts(data, filters=[['status', '=', 1]])
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[unread_domain_cnts.get(d, 0) for d in top_domains],
        y=top_domains,
        name='Unread articles',
        orientation='h',
    ))
    fig.add_trace(go.Bar(
        x=[archived_domain_cnts.get(d, 0) for d in top_domains],
        y=top_domains,
        name='Archived articles',
        orientation='h',
    ))
    fig.update_layout(
        title_text='Top Domains',
        barmode='stack',
        yaxis=dict(tickmode='linear'),  # to show ALL labels
    )
    return dcc.Graph(figure=fig)


def language_counts_plot(data: List[Dict]) -> dcc.Graph:
    pairs = list(get_language_counts(data).items())
    fig = go.Figure(
        data=[
            go.Pie(
                labels=[p[0] for p in pairs],
                values=[p[1] for p in pairs],
            ),
        ],
        layout_title_text="Languages",
    )
    return dcc.Graph(figure=fig)


def favorite_count_plot(data: List[Dict]) -> html.Div:
    res = get_favorite_count(data)
    return html.Div(
        [
            html.H2(children='Favorite', className='center-text'),
            html.H2(
                children=f"{res['count']} articles ({'%.2f' % (100.0 * res['percent'])} %)",
                className='center-text highlight',
            )
        ],
        className='favorite-div',
    )


def input_section() -> html.Div:
    return html.Div([
        html.Div([
            plot_two_columns(
                html.Label("Pocket Access Token", style=INPUT_SECTION_STYLE),
                dcc.Input(
                    id='input_pocket_access_token',
                    placeholder='Enter your Pocket Access Token',
                    value=ACCESS_TOKEN if ACCESS_TOKEN else '',
                    style=INPUT_SECTION_STYLE,
                ),
                width0_percent=20,
            ),
            plot_two_columns(
                html.Label("Number of records", style=INPUT_SECTION_STYLE),
                dcc.Slider(
                    id='input_pocket_number_of_records',
                    marks={i: str(i) for i in range(0, MAX_NUMBER_OF_RECORDS+1, 250)},
                    min=1, max=MAX_NUMBER_OF_RECORDS, step=250, value=250,
                ),
                width0_percent=20,
            ),
            plot_two_columns(
                html.Button('Reload', id='input_reload_button', n_clicks=0,
                            style={'font-size': '30px', 'background-color': 'coral'}),
                html.Div(id="number_of_records",
                         style={'font-size': '30px', 'color': 'blue'}),
                width0_percent=20,
            )
        ]),
    ])


def create_app(data: List[Dict] = None, server=None) -> dash.Dash:
    app = dash.Dash() if (server is None) else dash.Dash(server=server)
    app.index_string = DASH_APP_INDEX_STRING
    app.title = "Pocket Stats"
    app.layout = html.Div(style={}, children=[
        input_section(),
        html.Div(id='word_cloud_div', children=[]),
        html.Div(id='articles_over_time_div', children=[]),
        plot_two_columns(
            html.Div(id='word_counts_div', children=[]),
            html.Div(id='reading_time_div', children=[]),
        ),
        html.Div(id='domain_counts_div', children=[]),
        plot_two_columns(
            html.Div(id='language_counts_div', children=[]),
            html.Div(id='favorite_counts_div', children=[]),
        ),
    ])

    @app.callback(
        Output('number_of_records', 'children'),
        Output('word_cloud_div', 'children'),
        Output('articles_over_time_div', 'children'),
        Output('word_counts_div', 'children'),
        Output('reading_time_div', 'children'),
        Output('domain_counts_div', 'children'),
        Output('language_counts_div', 'children'),
        Output('favorite_counts_div', 'children'),
        Input(component_id='input_reload_button', component_property='n_clicks'),
        State(component_id='input_pocket_access_token', component_property='value'),
        State(component_id='input_pocket_number_of_records', component_property='value'),
    )
    def update_data(
        n_clicks: int,
        input_pocket_access_token: str,
        input_pocket_number_of_records: str,  # need to convert it to int
    ) -> Tuple[Any, Any, Any, Any, Any, Any, Any, Any]:
        if n_clicks == 0:
            return [None] * 8
        data = get_data(
            access_token=input_pocket_access_token,
            limit=input_pocket_number_of_records,
        )
        return (
            [f"Fetched {len(data)} records"],
            word_cloud_plot(data),
            articles_over_time_plot(data),
            word_counts_plot(data),
            reading_time_plot(data),
            domain_counts_plot(data),
            language_counts_plot(data),
            favorite_count_plot(data),
        )

    @app.callback(
        Output(component_id='reading-time-chart', component_property='figure'),
        Output(component_id='reading-time-needed', component_property='children'),
        Input(component_id='reading-speed', component_property='value'),
        Input(component_id='reading-minutes-daily', component_property='value'),
        State(component_id='input_pocket_access_token', component_property='value'),
        State(component_id='input_pocket_number_of_records', component_property='value'),
    )
    def update_reading_time_components(
        reading_speed: int,
        reading_minutes_daily: int,
        input_pocket_access_token: str,
        input_pocket_number_of_records: str,  # need to convert it to int
    ) -> Tuple[go.Figure, str]:
        data = get_data(
            access_token=input_pocket_access_token,
            limit=input_pocket_number_of_records,
        )
        return (get_reading_time_chart(data, reading_speed),
                get_reading_time_needed(data, reading_speed, reading_minutes_daily))

    return app
