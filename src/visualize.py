"""Visualize queried words" improper alignment."""
from math import log
import argparse
from plotly.graph_objs import Scatter, Layout, Figure
from plotly.graph_objs.layout import XAxis, YAxis, Margin
from plotly.offline import plot
from utils import load_pickle, lemma2metacode
from bitexts import AlignmentInfo
from align2graph import translator_lst, metacode2lemma_map_src, romaji2kanji_map, retrive_igraph, retrive_igraph_by_translator


def draw_plotly(*words):
    """Visuialize by plotly; default mode."""
    graph = retrive_igraph(*words)
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

    # Annotations
    vertex_label = graph.vs["node"]
    edge_label = graph.es["weight"]
    title = "; ".join(
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

    # Edge meta information as hover label
    def edge_hover():
        for e in graph.es:
            path = e["path"]
            count = e["weight"]
            hover_label = f"<b>{path}</b>: {count}<br><br>"
            for translator in translator_lst:
                label = f"<b>{romaji2kanji_map[translator]}</b>: {e[translator]}<br>"
                hover_label += label
            yield hover_label

    # Edge meta information as hover label
    def vertex_hover():
        for v in graph.vs:
            word = v["node"]
            count = v["weight"]
            meta_info = v["meta_attr"]
            node_type = v["node_type"]
            hover_label = f"<b>{word}</b>: {count}<br>"
            if node_type == 1:
                for info in meta_info:
                    hover_label += f"{info}<br>"
            else:
                for path_label in meta_info:
                    hover_label += f"<br><br><b>{path_label}:<b><br>"
                    for source_label in meta_info[path_label]:
                        hover_label += f"<br>{source_label}<br>"
                        for target_label in meta_info[path_label][
                                source_label]:
                            hover_label += f"{target_label[:30]}...<br>"
            yield hover_label

    # Figure construction
    trace1 = Scatter(
        x=Xe,
        y=Ye,
        mode="lines",
        line=dict(color="lightsteelblue", width=1),
        hoverinfo="none",
    )
    trace2 = Scatter(
        x=Xn,
        y=Yn,
        mode="markers+text",
        name="ntw",
        marker=dict(symbol=vertex_shape,
                    size=vertex_size,
                    color=vertex_color,
                    line=dict(color="white", width=0.5)),
        text=vertex_label,
        hoverinfo="text",
        hovertext=list(vertex_hover()),
    )
    edge_label = Scatter(
        x=Xe_label,
        y=Ye_label,
        mode="text",
        text=edge_label,
        textposition="bottom center",
        hoverinfo="text",
        hovertext=list(edge_hover()),
    )
    axis = dict(
        showline=False,  # hide axis line, grid, ticklabels and  title
        zeroline=False,
        showgrid=False,
        showticklabels=False,
        title="",
    )
    width = 1000
    height = 1000
    layout = Layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=10),
        showlegend=False,
        autosize=True,
        width=width,
        height=height,
        xaxis=XAxis(axis),
        yaxis=YAxis(axis),
        margin=Margin(
            l=40,
            r=40,
            b=85,
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
                y=-0.1,
                xanchor="left",
                yanchor="bottom",
                font=dict(size=10),
            )
        ],
    )

    data = [trace1, trace2, edge_label]
    fig = Figure(data=data, layout=layout)

    return fig


def draw_plotly_by_translator(*words):
    """Visuialize by plotly; default mode."""
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
    title = "; ".join(
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
        line=dict(color="lightsteelblue", width=1),
        hoverinfo="none",
    )
    trace2 = Scatter(
        x=Xn,
        y=Yn,
        mode="markers+text",
        name="ntw",
        marker=dict(symbol=vertex_shape,
                    size=vertex_size,
                    color=vertex_color,
                    line=dict(color="white", width=0.5)),
        text=vertex_label,
        hoverinfo="none",
    )
    edge_label = Scatter(
        x=Xe_label,
        y=Ye_label,
        mode="text",
        text=edge_label,
        hoverinfo="none",
    )
    axis = dict(
        showline=False,  # hide axis line, grid, ticklabels and  title
        zeroline=False,
        showgrid=False,
        showticklabels=False,
        title="",
    )
    width = 600
    height = 600
    layout = Layout(
        title=title,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=10),
        showlegend=False,
        autosize=True,
        width=width,
        height=height,
        xaxis=XAxis(axis),
        yaxis=YAxis(axis),
        margin=Margin(
            l=40,
            r=40,
            b=85,
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
                font=dict(size=10),
            )
        ],
    )

    data = [trace1, trace2, edge_label]
    fig = Figure(data=data, layout=layout)

    return fig


def main(args):
    metacode2lemma_map = load_pickle("../cache/metacode2lemma_src.pkl")
    words = [lemma2metacode(word, metacode2lemma_map) for word in args.words]
    if args.by == "word":
        fig = draw_plotly(*words)
    elif args.by == "translator":
        fig = draw_plotly_by_translator(*words)
    plot(fig, filename=f"../artifacts/{';'.join(words)}.html")


def cli_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b",
                        "--by",
                        choices=["word", "translator"],
                        help="plot method")
    parser.add_argument("-w", "--words", nargs="+", help="words to query")
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli_main()
