"""Input bitext ID, return alignment table."""
import argparse
from typing import Literal
import pandas as pd
from plotly.graph_objects import Figure, Heatmap, Layout
from plotly.offline import plot
from utils import load_pickle, lemma2metacode

DB = load_pickle("../cache/bitexts.db")
translator_lst = DB.translators
metacode2lemma_map_src = load_pickle("../cache/metacode2lemma_src.pkl")
metacode2lemma_map_tar = load_pickle("../cache/metacode2lemma_tar.pkl")

Direction = Literal["source2target", "target2source", "bidirection",
                    "improper"]
Translator = Literal[translator_lst]


def alignment_table(word: str,
                    translator: Translator,
                    direction: Direction = "bidirection"):
    """Return alignment chessboard."""
    word = lemma2metacode(word, metacode2lemma_map_src)
    bitexts = DB.query_bitext_by_translator(translator)
    print("Query results:")
    candidates = [bitext for bitext in bitexts if word in bitext.source]
    multi_choice = {}
    for idx, candidate in enumerate(candidates, 1):
        print(f"{idx:2d}: {candidate}")
        multi_choice[idx] = candidate
    choice = int(input("Select one poem:"))
    bitext = multi_choice[choice]
    if direction == "source2target":
        alignment = bitext.alignment_source2target
    elif direction == "target2source":
        alignment = [i[::-1] for i in bitext.alignment_target2source]
    elif direction == "bidirection":
        alignment = list(bitext.proper_alignment_idx())
    else:
        alignment = list(bitext.improper_alignment_idx())
    heatmap = {}
    for i, src in enumerate(bitext.source):
        src = str(i + 1) + '.' + metacode2lemma_map_src[src]
        heatmap[src] = {}
        for j, tar in enumerate(bitext.target):
            tar = str(j + 1) + '.' + metacode2lemma_map_tar[tar]
            if (i, j) in alignment:
                heatmap[src][tar] = 1
            else:
                heatmap[src][tar] = 0
    heatmap = pd.DataFrame(heatmap).T
    poem_id = bitext.poem
    return poem_id, heatmap


def visualize_heatmap(heatmap):
    """Plot heatmap.
    
    :param heatmap: pandas.DataFrame
    """
    col_name = heatmap.columns
    row_name = heatmap.index
    table = heatmap.values.tolist()
    layout = Layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis_scaleanchor="x",
        height=600,
    )

    fig = Figure(
        Heatmap(
            z=table,
            x=col_name,
            y=row_name,
            type = 'heatmap',
            colorscale = ['black', 'white'],
            # labels=dict(x="Source text", y="Target text"),
        ),
        layout = layout,
    )
    fig.update_traces(showlegend=False, showscale=False)
    return fig


def main(args):
    poem_id, heatmap = alignment_table(args.word, args.translator, args.mode)
    fig = visualize_heatmap(heatmap)
    heatmap.to_csv(f"../artifacts/{poem_id}-{args.translator}-{args.mode}.csv")
    plot(fig, filename=f"../artifacts/{'-'.join([poem_id, args.translator, args.mode])}.html")


def cli_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--word", help="word")
    parser.add_argument("-t", "--translator", help="translator")
    parser.add_argument("-m", "--mode", help="alignment mode")
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli_main()
