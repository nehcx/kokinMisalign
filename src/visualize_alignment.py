"""Input bitext ID, return alignment table."""
import argparse
from typing import Literal
from numpy import NaN
import pandas as pd
from plotly.graph_objects import Figure, Heatmap, Scatter, Layout
from plotly.graph_objs.layout import XAxis, YAxis, Margin
from plotly.offline import plot
from utils import load_pickle, lemma2metacode

DB = load_pickle("../cache/bitexts.db")
translator_lst = DB.translators
metacode2lemma_map_src = load_pickle("../cache/metacode2lemma_src.pkl")
metacode2lemma_map_tar = load_pickle("../cache/metacode2lemma_tar.pkl")

Direction = Literal["source2target", "target2source", "bidirection",
                    "improper"]
Translator = Literal[translator_lst]


def query(word: str, translator: Translator):
    """Return bitext dataframe."""
    bitexts = DB.query_bitext_by_translator(translator)    
    candidates = [bitext for bitext in bitexts if word in bitext.source]
    return candidates

def alignment_table(poem, translator, word):
    """Return alignment chessboard."""
    bitexts = DB.query_bitext_by_translator(translator)    
    bitext = [bitext for bitext in bitexts if bitext.poem == poem][0]
    alignment_1 = bitext.alignment_source2target  # source to target
    alignment_2 = [i[::-1] for i in bitext.alignment_target2source]  # target to source
    alignment_3 = list(bitext.proper_alignment_idx())  # intersection
    alignment_4 = list(bitext.improper_alignment_idx())  # misaligned
    heatmap = {}
    targets = []
    for i, src in enumerate(bitext.source):
        if src == word:
            src = str(i + 1) + "." + metacode2lemma_map_src[src]
            targets.append(src)
        else:
            src = str(i + 1) + "." + metacode2lemma_map_src[src]
        heatmap[src] = {}
        for j, tar in enumerate(bitext.target):
            tar = str(j + 1) + "." + metacode2lemma_map_tar[tar]
            if (i, j) in alignment_3:
                heatmap[src][tar] = 2.5
            elif (i, j) in alignment_4:
                heatmap[src][tar] = 1.5
            elif (i, j) in alignment_1:
                heatmap[src][tar] = 0.5          
            elif (i, j) in alignment_2:
                heatmap[src][tar] = 1.5
            else:
                heatmap[src][tar] = None
    heatmap = pd.DataFrame(heatmap).T
    poem_id = bitext.poem
    return poem_id, heatmap, targets


def visualize_heatmap(heatmap, targets):
    """Plot heatmap.
    
    :param heatmap: pandas.DataFrame
    """
    # contents
    col_name = heatmap.columns.tolist()
    row_name = heatmap.index[::-1].tolist()
    table = heatmap.values.tolist()[::-1]
    # legend color scaler
    def _discrete_colorscale(bvals, colors):
        if len(bvals) != len(colors)+1:
            raise ValueError(
                "len(boundary values) should be equal to  len(colors)+1"
            )
        bvals = sorted(bvals)     
        nvals = [(v-bvals[0])/round(bvals[-1]-bvals[0],5) for v in bvals]  #normalized values
        dcolorscale = [] #discrete colorscale
        for k in range(len(colors)):
            dcolorscale.extend([[nvals[k], colors[k]], [nvals[k+1], colors[k]]])
        return dcolorscale
    # Intervals
    bvals = [0, 1, 2, 3]
    colors = ["lightyellow",
              "pink",
              "gray"]
    dcolorsc = _discrete_colorscale(bvals, colors)
    # ticks
    tickvals = [0.85, 1.5, 2.15]
    ticktext = ["Source-to-target model", 
                "Target-to-source model (possible misalignment)",
                "Intersection of 2 models"]
    # hover
    int2text_dict = {
        0.5: "<b>Inferred by source-to-target model<b>:<br>",
        1.5: "<b>Inferred by target-to-source model<b>:<br>",
        2.5: "<b>Inferred by intersection model<b>:<br>",
    }
    text_table = [
        [
            "" if pd.isnull(model) else int2text_dict[model] + 
            f"source: {source}<br>" + f"target: {target}"
         for model, target in zip(row, col_name)
        ]
        for row, source in zip(table, row_name)
    ]
    # layout
    xaxis = dict(
        showline=False,  # hide axis line, grid, ticklabel
        zeroline=False,
        showgrid=False,
        showticklabels=True,
        title="Target text",
    )
    yaxis = dict(
        showline=False,  # hide axis line, grid, ticklabel
        zeroline=False,
        showgrid=False,
        showticklabels=True,
        title="Source text",
    )
    layout = Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_scaleanchor="y",
        height=500,
        width=1000,
        xaxis=XAxis(xaxis),
        yaxis=YAxis(yaxis),
        margin=Margin(
            l=40,
            r=40,
            b=40,
            t=0,
        ),
        hovermode="closest",
    )
    # fig
    fig = Figure(
        Heatmap(
            z=table,
            x=col_name,
            y=row_name,
            xgap=5,
            ygap=5,
            type = "heatmap",
            hoverinfo="none",
            hoverongaps = False,    
            showlegend = False,    
            showscale = False,
        ),
        layout = layout
    )
    # line
    for target in targets:
        idx = row_name.index(target)
        fig.add_trace(
            Scatter(
                x=col_name,
                y=[row_name[idx]] * len(col_name),
                mode="lines",
                name="queried word",
                line=dict(
                    dash="dot",
                    color="lightsteelblue",
                ),
                hoverinfo="text",
                text=[row_name[idx]] * len(col_name),
            )
        )
    # heatmap
    fig.add_trace(
        Heatmap(
            z=table,
            x=col_name,
            y=row_name,
            xgap=2,
            ygap=2,
            type = "heatmap",
            colorscale = dcolorsc,
            colorbar = dict(
                thickness=5, 
                tickvals=tickvals, 
                ticktext=ticktext,
                title="Inferred by",
                orientation="h",
                y=1,
                yanchor="bottom",
            ),
            text = text_table,
            hoverinfo = "text",    
            hoverongaps = False,    
            showlegend = False,    
            showscale = True,
            # labels=dict(x="Source text", y="Target text"),
        )
    )
    return fig


def main(args):
    print("Query results:")
    word = lemma2metacode(args.word, metacode2lemma_map_src)
    candidates = query(word, args.translator)
    multi_choice = {}
    for idx, candidate in enumerate(candidates, 1):
        print(f"{idx:2d}: {candidate}")
        multi_choice[idx] = candidate
    choice = int(input("Select one poem:"))
    bitext = multi_choice[choice]
    poem_id, heatmap, targets = alignment_table(bitext.poem, 
                                                bitext.translator, 
                                                word)
    fig = visualize_heatmap(heatmap, targets)
    heatmap.to_csv(f"../artifacts/{poem_id}-{args.translator}-{args.mode}.csv")
    plot(fig, 
         filename=f"""
         ../artifacts/{'-'.join([poem_id, args.translator, args.mode])}.html
         """
         )


def cli_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--word", help="word")
    parser.add_argument("-t", "--translator", help="translator")
    parser.add_argument("-m", "--mode", help="alignment mode")
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli_main()

