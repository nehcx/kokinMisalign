"""Dash board."""
import pandas as pd
from plotly.graph_objs import Scatter, Layout, Figure
from plotly.graph_objs.layout import XAxis, YAxis, Margin
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from bitexts import AlignmentInfo
from utils import load_pickle, lemma2metacode
from visualize_indivisual import draw_plotly_by_translator_by_poem
from visualize_aggregate_translator import draw_plotly_by_translator
from visualize_alignment import query, alignment_table, visualize_heatmap 

fullname2id_map = {
    "[金子] Kaneko, Motoomi (1933)": "kaneko",
    "[窪田] Kubota, Utsubo (1960)": "kubota",
    "[松田] Matsuda, Takeo (1968)": "matsuda",
    "[小沢] Ozawa, Masao (1971)": "ozawa",
    "[竹岡] Takeoka, Masao (1976)": "takeoka",  
    "[奥村] Okumura, Tsuneya (1978)": "okumura",
    "[久曽神] Kyusojin, Hitachi (1979)": "kyusojin",
    "[小町谷] Komachiya, Teruhiko (1982)": "komachiya",
    "[小島・新井] Kojima, Noriyuki and Arai, Eizo (1989)": "kojimaarai",
    "[片桐] Katagiri, Yoichi (1998)": "katagiri",
}
translator_lst = fullname2id_map.keys()
metacode2lemma_map_src = load_pickle("../cache/metacode2lemma_src.pkl")
word_lst = [k + ":" + v  for k, v in metacode2lemma_map_src.items() if k[:8] == "BG-01-55"]
word_lst.sort()
with open("../README-app.md", 'r') as f: 
    readme = f.read()


def _blank(width, height, text, font_size): 
    Xn = [0]
    Yn = [0]
    trace = Scatter(
        x=Xn,
        y=Yn,
        mode="text",
    )
    annotation = text
    data = [trace]
    axis = dict(
        showline=False, 
        zeroline=False,
        showgrid=False,
        showticklabels=False,
        title="",
    )
    layout = Layout(
        # title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=16),
        showlegend=False,
        autosize=True,
        width=width,
        height=height,
        xaxis=XAxis(axis),
        yaxis=YAxis(axis),
        margin=Margin(
            l=0,
            r=0,
            b=85,
            t=40,
        ),
        hovermode="closest",
        annotations=
[
            dict(
                showarrow=False,
                text=annotation,
                xref="paper",
                yref="paper",
                x=0,
                y=0,
                xanchor="left",
                yanchor="bottom",
                font=dict(size=font_size),
            )
        ],
    )

    fig = Figure(data=data, layout=layout)
    return fig

app = dash.Dash(
    __name__,
    meta_tags=[
        {
            "name": "viewport", 
            "content": "width=device-width, initial-scale=1"
        }
    ],
)

app.layout = html.Div(
    children=[
        # title
        html.H1(
            children="""
            Dashboard for visualizing word alignment and misalignment between 
            classical poetic Japanese and its contemporary translations
            """,
        ),
        # query and intro
        dcc.Tabs(
            id="intro-and-query-tabs",
            value="what-is",
            parent_className="custom-tabs",
            className="custom-tabs-container",
            children=[
                dcc.Tab(
                    label="About",
                    value="what-is",
                    className="custom-tab",
                    selected_className="custom-tab--selected",
                    children=html.Div(
                        className="control-tab",
                        children=[
                            dcc.Markdown(readme),
                        ],
                    ),
                ),
                dcc.Tab(
                    label="Query",
                    value="alignment-tab-select",
                    className="custom-tab",
                    selected_className="custom-tab--selected",
                    children=html.Div(
                        className="app-controls-block",
                        children=[
                            # query word and translator
                            html.Div(
                                [
                                    html.Br(),
                                    html.Div([
                                        html.Label("Word:"),
                                        dcc.Dropdown(
                                            id="target",
                                            options=[
                                                {"label": i, "value": i} 
                                                for i in word_lst
                                            ],
                                            value="BG-01-5520-05-0106:女郎花",
                                            multi=False,
                                        ),
                                    ],
                                             style={
                                                 "width": "45%", 
                                                 "display": "inline-block",
                                             }
                                             ),

                                    html.Div([
                                        html.Label("Translator:"),
                                        dcc.Dropdown(
                                            id="translator",
                                            options=[
                                                {"label": i, "value": i} 
                                                for i in translator_lst
                                            ],
                                            value="[金子] Kaneko, Motoomi (1933)",
                                            multi=False,
                                        ),
                                    ],
                                             style={
                                                 "width": "45%", 
                                                 "float": "right", 
                                                 "display": "inline-block",
                                             }
                                             ),
                                ],
                            ),
                            # query specific poem
                            html.Br(),
                            html.Div(
                                [
                                    html.Label(
                                        """
                                        Query results (click cell to visualize 
                                        alignment and collective misalignment 
                                        network of the bitext on the selected 
                                        row):
                                        """
                                    ),
                                    dash_table.DataTable(
                                        id="datatable-paging",
                                        columns=[
                                            {"name": i, "id": i} for i in 
                                            ["poem", "queried word", 
                                             "source text", "target text"]
                                        ],
                                        page_current=0,
                                        page_size=3,
                                        page_action="custom",
                                        style_cell_conditional=[
                                            {"if": {"column_id": "target text"},                                        
                                             "width": "45%"},
                                            {"if": {"column_id": "source text"},                                        
                                             "width": "40%"},
                                            {"if": {"column_id": "poem"},                                        
                                             "width": "5%"},
                                            {"if": {"column_id": "queried word"},                                        
                                             "width": "10%"},
                                        ],
                                        style_cell={
                                            "overflow": "hidden",
                                            "textOverflow": "ellipsis",
                                            "maxWidth": 0,
                                        },
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        ),

        html.Br(),
        dcc.Tabs(
            id="result-tabs",
            value="network-tab-select",
            parent_className="custom-result-tabs",
            className="custom-result-tabs-container",
            children=[
                dcc.Tab(
                    label="Word alignment visualization",
                    value="alignment-tab-select",
                    className="custom-tab",
                    selected_className="custom-tab--selected",
                    children=html.Div(
                        className="result-tab",
                        children=[
                            html.Div(
                                dcc.Graph(id="alignment-graph"),
                                style={
                                    "width": "100%", 
                                    "display": "inline-block",
                                },
                            ),
                        ],
                    ),
                ),

                # html.Hr(),
                dcc.Tab(
                    label="Collective misalignment network visualization",
                    value="network-tab-select",
                    className="custom-tab",
                    selected_className="custom-tab--selected",
                    children=html.Div(
                        className="result-tab",
                        children=[ 
                            html.Br(),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            # html.Label("Selected poem"),
                                            dcc.Graph(
                                                id="individual-network-graph"
                                            ), 
                                        ],       
                                        style={
                                            "width": "50%", 
                                            "float": "left", 
                                            "display": "inline-block",
                                        },
                                    ),

                                    html.Div(
                                        [
                                            # html.Label("All queried poems"),
                                            dcc.Graph(
                                                id="translator-network-graph"
                                            ), 
                                        ],       
                                        style={
                                            "width": "50%", 
                                            "float": "right", 
                                            "display": "inline-block",
                                        },
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        ),
    ],
                      )


# Data table
@app.callback(
    [Output("datatable-paging", "page_current"),
     Output("datatable-paging", "page_count"),
     Output("datatable-paging", "data")],
    [Input("datatable-paging", "page_current"),
     Input("datatable-paging", "page_size"),
     Input("target", "value"),
     Input("translator", "value")],
    [State("datatable-paging", "data")]
)
def update_table(page_current, page_size, target, translator, table_data):
    target, word = target.split(":")
    translator = fullname2id_map[translator]
    candidates = query(target, translator)
    page_count = len(candidates) // page_size + 1
    candidate_df = pd.DataFrame({
        "poem": [candidate.poem for candidate in candidates],
        "source text": [candidate.source_surface for candidate in candidates],
        "target text": [candidate.target_surface for candidate in candidates],
        "queried word": [word for candidate in candidates],
    })
    data = candidate_df.iloc[
        page_current*page_size:(page_current+1)*page_size
    ].to_dict("records")
    if table_data is not None:
        try: 
            table_data[0]
        except:
            page_current = page_count - 1
    return page_current, page_count, data


# Alignment visualization and individual poem network visualization
@app.callback(
    [Output("alignment-graph", "figure"),
     Output("individual-network-graph", "figure")],
    [Input("datatable-paging", "active_cell"),
     Input("datatable-paging", "page_current"),
     Input("datatable-paging", "page_size"),
     Input("translator", "value"),
     Input("target", "value")],
    [State("datatable-paging", "data")]
)
def update_alignment_and_individual_network_graph(
        active_cell, page_current, page_size, 
        translator, target, table_data):
    try:
        target, word = target.split(":")
        translator = fullname2id_map[translator]
        if active_cell:
            row = active_cell["row"]
            queied_word = table_data[row]["queried word"]
            if queied_word == word:
                idx = table_data[row]["poem"]
                text = table_data[row]["source text"]
            else:
                candidates = query(target, translator)    
                current_candidate = candidates[page_current*page_size]    
                idx = current_candidate.poem
                text = current_candidate.source_surface
        else:
            candidates = query(target, translator)    
            current_candidate = candidates[page_current*page_size]    
            idx = current_candidate.poem
            text = current_candidate.source_surface
        _, heatmap, targets = alignment_table(idx, translator, target)
        fig_alignment = visualize_heatmap(heatmap, targets)
        fig_alignment.update_layout(transition_duration=500)
        fig_individual_network = draw_plotly_by_translator_by_poem(target, idx)
        fig_individual_network.update_layout(
            title = f"<span style='font-size: 14px;'>{target} {word}</span>" + 
            "<br>" +
            f"<span style='font-size: 10px;'>{text} -古今{idx}</span>"
        )
        fig_individual_network.update_layout(transition_duration=500)
        return fig_alignment, fig_individual_network
    except:
        return (_blank(1000, 600, "Queried word was not found.", 12),
                _blank(500, 600, "Queried word was not found.", 12))


# Global network visualization
@app.callback(
    Output("translator-network-graph", "figure"),
    [Input("target", "value")]
)
def update_translator_network(target):
    try:
        target = target.split(":")[0]
        fig = draw_plotly_by_translator(target)
        fig.update_layout(transition_duration=500)
        return fig
    except:
        return _blank(500, 600, "Queried word was not found.", 12)


if __name__ == "__main__":
    app.run_server(debug=True)
