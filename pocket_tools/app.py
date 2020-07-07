import random
import plotly
import pandas as pd
from typing import List, Dict
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px

from data import load_cache, count_words_in_title, get_word_counts, get_reading_time, get_domain_counts
from data import get_added_time_series, get_archived_time_series, get_language_counts, get_favorite_count
from constants import DEFAULT_READING_SPEED


def word_cloud_plot(data: List[Dict]) -> html.Div:
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
    return html.Div([
        dcc.Graph(id='word-cloud', figure=fig)
    ])


def articles_over_time_plot(data: List[Dict], should_cumsum: bool = True) -> html.Div:
    df = get_added_time_series(data)
    archived_df = get_archived_time_series(data)
    if len(archived_df) > 0:
        df = pd.merge(df, archived_df, how='outer', left_index=True, right_index=True)
    if should_cumsum:
        df.fillna(0, inplace=True)
        df = df.cumsum()
    fig = px.line(df, labels={'index': 'Date', 'value': 'Number of articles'})
    return dcc.Graph(id='time_series', figure=fig)


def word_counts_plot(data: List[Dict]) -> html.Div:
    word_cnts = get_word_counts(data)
    fig = px.histogram(x=word_cnts, labels={'x': 'Number of words'})
    return dcc.Graph(id='word-counts', figure=fig)


def reading_time_plot(data: List[Dict]) -> html.Div:
    reading_times = get_reading_time(data)
    fig = px.histogram(
        x=reading_times,
        labels={'x': f'Estimated reading time (minutes) with reading speed = {DEFAULT_READING_SPEED} wpm'}
    )
    return dcc.Graph(id='reading-time', figure=fig)


def domain_counts_plot(data: List[Dict], limit: int = 20) -> dcc.Graph:
    pairs = list(get_domain_counts(data).items())
    pairs.sort(key=lambda p: -p[1])  # sort desc by count
    pairs = pairs[:limit]  # display top items only
    pairs.reverse()  # because px.bar display the items in a reversed order
    fig = px.bar(x=[p[1] for p in pairs],
                 y=[p[0] for p in pairs],
                 orientation='h', labels={'x': 'Number of articles', 'y': 'Domain'})
    return dcc.Graph(id='domain-counts', figure=fig)


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
    return dcc.Graph(id='language-counts', figure=fig)


def favorite_count_plot(data: List[Dict]) -> html.Div:
    res = get_favorite_count(data)
    return html.Div([
        html.H1(children='Favorite', style={'textAlign': 'center'}),
        html.H1(
            children=f"{res['count']} articles ({'%.2f' % res['percent']} %)",
            style={
                'textAlign': 'center',
                'color': 'orange',
            }
        ),
    ])


if __name__ == '__main__':
    data = load_cache()
    app = dash.Dash()
    app.layout = html.Div(style={}, children=[
        word_cloud_plot(data),
        articles_over_time_plot(data),
        word_counts_plot(data),
        reading_time_plot(data),
        domain_counts_plot(data),
        language_counts_plot(data),
        favorite_count_plot(data),
    ])
    app.run_server(debug=True)  # TODO: add command line option --debug
