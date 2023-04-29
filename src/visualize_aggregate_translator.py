"""Visualize queried words improper alignment by translators."""
from math import log
import argparse
from plotly.graph_objs import Scatter, Layout, Figure
from plotly.graph_objs.layout import XAxis, YAxis, Margin
from plotly.offline import plot
from utils import load_pickle, lemma2metacode
from bitexts import AlignmentInfo
from align2graph import translator_lst, metacode2lemma_map_src, romaji2kanji_map, retrive_igraph_by_translator


def draw_plotly_by_translator(*words):
    """Visuialize by plotly; by-translator mode."""
    graph = retrive_igraph_by_translator(*words)
    E = [e.tuple for e in graph.es]  # TupleList of edges
    n_label = len(graph.vs)  # Node number
    layt = graph.layout("kk")  # Hamada-Kawai layout

    # Basic config
    Xn = [layt[k][0] for k in range(n_label)]
    Yn = [layt[k][1] for k in range(n_label)]
    Xe = []
    Ye = []
    Xe_label = []
    Ye_label = []
    for e in E:
        Xe += [layt[e[0]][0], layt[e[1]][0], None]
        Ye += [layt[e[0]][1], layt[e[1]][1], None]
        Xe_label.append((layt[e[0]][0] + layt[e[1]][0]) / 2)
        Ye_label.append((layt[e[0]][1] + layt[e[1]][1]) / 2)

    # Color, size, shape
    vertex_type_shape_dict = {
        "source": "circle",
        "target": "square",
        "dublicate": "square"
    }
    vertex_type_color_dict = {
        "source": "mistyrose",
        "target": "lightgray",
        "dublicate": "lightyellow"
    }
    vertex_size = [log(freq + 1) * 10 for freq in graph.vs["weight"]]
    # vertex_label_size = [log(freq + 1) * 9 for freq in graph.vs["weight"]]
    vertex_shape = [
        vertex_type_shape_dict[type_label]
        for type_label in graph.vs["type_label"]
    ]
    vertex_color = [
        vertex_type_color_dict[type_label]
        for type_label in graph.vs["type_label"]
    ]
    vertex_label = [
        f"<b>{v['node']}<b>" if v["node_type"] == 1 else v["node"]
        for v in graph.vs
    ]

    # Annotations
    edge_label = graph.es["weight"]
    title = ";<br>".join(
        [f"{word} {metacode2lemma_map_src[word]}" for word in words])

    # Betweenness centrality
    def betweenness_centrality():
        for v, betweenness in zip(graph.vs, graph.betweenness()):
            if v["node_type"] == 1:
                continue
            yield (v["node"], betweenness)

    betweenness = sorted(list(betweenness_centrality()),
                         key=lambda x: x[-1],
                         reverse=True)
    annotation_lst = [f"<b>{i[0]}<b>: {i[-1]:2.2f}" for i in betweenness]
    annotation = "top-5 betweenness centrality: " + "; ".join(
        annotation_lst[:5])

    # Figure construction
    trace1 = Scatter(
        x=Xe,
        y=Ye,
        mode="lines",
        line=dict(
            color="lightsteelblue",
            width=1,
        ),
        showlegend=False,
        hoverinfo="none",
    )
    trace2 = Scatter(
        x=Xn,
        y=Yn,
        mode="markers+text",
        name="ntw",
        marker=dict(
            symbol=vertex_shape,
            size=vertex_size,
            color=vertex_color,
            line=dict(
                color="white",
                width=0.5,
            ),
        ),
        showlegend=False,
        text=vertex_label,
        hoverinfo="none",
    )
    edge_label = Scatter(
        x=Xe_label,
        y=Ye_label,
        mode="text",
        showlegend=False,
        text=edge_label,
        hoverinfo="none",
    )
    custom_legend_1 = Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(
            size=16,
            symbol="circle",
            color="mistyrose",
        ),
        legendgroup="queried word",
        showlegend=True,
        name="queried word",
    )
    custom_legend_2 = Scatter(
        x=[None],
        y=[None],
        mode="markers",
        marker=dict(
            size=16,
            symbol="square",
            color="lightgray",
        ),
        legendgroup="misalignment candidate",
        showlegend=True,
        name="misalignment candidate",
    )
    custom_legend_3 = Scatter(
        x=[None],
        y=[None],
        mode="lines",
        line=dict(
            color="lightsteelblue",
            width=1,
        ),
        legendgroup="possibly misaligned relation",
        showlegend=True,
        name="""
        possibly misaligned relation, 
        number indicates misalignment candidate count
        """,
    )
    data = [
        trace1, trace2, edge_label, custom_legend_1, custom_legend_2,
        custom_legend_3
    ]
    axis = dict(
        showline=False,  # hide axis line, grid, ticklabels and  title
        zeroline=False,
        showgrid=False,
        showticklabels=False,
        title="",
    )
    width = 450
    height = 500
    layout = Layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=10),
        # showlegend=False,
        autosize=True,
        width=width,
        height=height,
        xaxis=XAxis(axis),
        yaxis=YAxis(axis),
        margin=Margin(
            l=0,
            r=0,
            b=0,
            t=40,
        ),
        hovermode="closest",
        annotations=[
            dict(
                showarrow=False,
                text=annotation,
                xref="paper",
                yref="paper",
                x=0,
                y=0,
                xanchor="left",
                yanchor="bottom",
                font=dict(size=8),
            )
        ],
    )

    fig = Figure(data=data, layout=layout)
    fig.update_layout(legend=dict(orientation="h",
                                  entrywidth=130,
                                  yanchor="top",
                                  y=0,
                                  xanchor="left",
                                  x=0,
                                  font=dict(size=8)))

    return fig


def main(args):
    metacode2lemma_map = load_pickle("../cache/metacode2lemma_src.pkl")
    codes = [lemma2metacode(word, metacode2lemma_map) for word in args.words]
    fig = draw_plotly_by_translator(*codes)
    fig.update_layout(
        title='',
        margin=Margin(
            l=0,
            r=0,
            b=0,
            t=0,
        ),
        # width=600,
        # height=700,
        font=dict(size=14)
    )
    plot(fig, filename=f"../artifacts/{'-'.join(args.words)}.html")
    fig.write_image(f"../artifacts/{';'.join(args.words)}.svg")


def cli_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--words", nargs="+", help="words to query")
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli_main()
