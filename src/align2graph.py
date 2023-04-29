"""From alignment info summary to generate graph."""
import re
import igraph as ig
from dataclasses import astuple, asdict
from utils import load_pickle
import bitexts

DB = load_pickle("../cache/bitexts.db")
translator_lst = DB.translators
metacode2lemma_map_src = load_pickle("../cache/metacode2lemma_src.pkl")
metacode2lemma_map_tar = load_pickle("../cache/metacode2lemma_tar.pkl")
romaji2kanji_map = {
    "kaneko": "金子",
    "katagiri": "片桐",
    "kojimaarai": "小島・新井",
    "komachiya": "小町谷",
    "kubota": "窪田",
    "kyusojin": "久曽神",
    "matsuda": "松田",
    "okumura": "奥村",
    "ozawa": "小沢",
    "takeoka": "竹岡"
}


def _filter(alignment_info_lst):
    """To remove edges that contain the same nodes with source nodes and stop pos."""
    for alignment_info in alignment_info_lst:
        source, target = alignment_info.alignment
        # BG-16: symbols
        # BG-0[456789]: words that are not nouns, verbs or adjectives
        # BG-03-1000: demonstratives
        pattern = re.compile(r'BG-16|BG-0[456789]|BG-03-1000')
        if pattern.match(target):
            continue
        if source[3:15] == target[3:15]:
            continue
        yield alignment_info

def retrive_igraph(*source_words):
    """Retrive igraph format data from alignment summary.

    :return graph: igraph-converted information.
    """
    target_word_set = set()
    alignment_lst = DB.query_improper_alignment_by_word(*source_words)    
    alignment_lst = list(_filter(alignment_lst))
    alignment_summary = bitexts.AlignmentSummary(alignment_lst)
    edge_info = alignment_summary.summary  # For edges' annotation

    # Aligned target word generator
    def target_words():
        for info in edge_info:
            target_word = info.alignment[1]
            if target_word in target_word_set:
                continue
            target_word_set.add(target_word)
            yield target_word

    # Source word node generator
    def source_nodes():
        for word in source_words:
            name = word
            node = metacode2lemma_map_src[word]
            node_type = 1
            type_label = "source"
            weight = 0
            meta_attr = []
            info_lst = alignment_summary.query_details_by_source(word)
            for info in info_lst:
                weight += 1
                surface = f"{int(info.poem):04d}: {info.source_surface}"
                if surface in meta_attr:
                    continue
                meta_attr.append(surface)
            yield (name, node, node_type, type_label, weight, meta_attr)

    # Target word node generator
    def target_nodes():
        for word in target_words():
            name = word
            node = metacode2lemma_map_tar[word]
            node_type = 2
            type_label = "target"
            weight = 0
            meta_attr_dict = {}
            info_lst = alignment_summary.query_details_by_target(word)
            for info in info_lst:
                weight += 1
                source_node = info.alignment[0]
                target_node = info.alignment[1]
                source_metacode = source_node.split("-")
                target_metacode = target_node.split("-")
                if source_metacode[:4] == target_metacode[:4]:
                    node_type = 3
                    type_label = "dublicate"
                path = "{} <= {}".format(metacode2lemma_map_src[source_node],
                                         metacode2lemma_map_tar[target_node])
                if path not in meta_attr_dict:
                    meta_attr_dict[path] = {}
                source = f"[Source text {int(info.poem):04d}] {info.source_surface}"
                target = f"{romaji2kanji_map[info.translator]}: {info.target_surface}"
                if source not in meta_attr_dict[path]:
                    meta_attr_dict[path][source] = [target]
                else:
                    meta_attr_dict[path][source].append(target)
            yield (name, node, node_type, type_label, weight, meta_attr_dict)

    # Edge generator with detailed information
    def edges():
        for info in edge_info:
            info = astuple(info)
            weight = info[1]
            source_node = info[0][0]
            target_node = info[0][1]
            path = "{} <= {}".format(metacode2lemma_map_src[source_node],
                                     metacode2lemma_map_tar[target_node])
            weight = info[1]
            fields = [f"{i:2d} ({i/weight*100:000.1f}%)" for i in info[2:]]
            yield (source_node, target_node, weight, path, *fields)

    # Igraph construction
    node_lst = list(source_nodes()) + list(target_nodes())
    edge_lst = list(edges())
    graph = ig.Graph.TupleList(edge_lst,
                               directed=False,
                               edge_attrs=["weight", "path", *translator_lst])
    for node_attr in node_lst:
        name, node, node_type, type_label, weight, meta_attr_dict = node_attr
        for v in graph.vs:
            if v["name"] != name:
                continue
            v["node"] = node
            v["node_type"] = node_type
            v["type_label"] = type_label
            v["weight"] = weight
            v["meta_attr"] = meta_attr_dict

    return graph


def retrive_igraph_by_translator(*source_words):
    """Retrive igraph format data with translator attension.

    :return graph: igraph-converted information.
    """
    target_word_set = set()
    source_word_translator_set = set()
    alignment_lst = DB.query_improper_alignment_by_word(*source_words)    
    alignment_lst = list(_filter(alignment_lst))
    alignment_summary = bitexts.AlignmentSummary(alignment_lst)
    edge_info = alignment_summary.alignment_info  # For edges' annotation

    # Edge by translator generator
    def edge_by_translator():
        for stat in alignment_summary.summary:
            source_word = stat.alignment[0]
            target_word = stat.alignment[1]
            stat = asdict(stat)
            for (key, value) in stat.items():
                if (key == "alignment") or (key == "total"):
                    continue
                source_node = f"{source_word}-{key}"
                target_node = target_word
                weight = value
                if weight == 0:
                    continue
                yield (source_node, target_node, weight)

    # Aligned target word generator
    def target_words():
        for info in edge_info:
            target_word = info.alignment[1]
            if target_word in target_word_set:
                continue
            target_word_set.add(target_word)
            yield target_word

    # Source word with translator coding generator
    def source_words_by_translator():
        for word in source_words:
            info_lst = alignment_summary.query_details_by_source(word)
            for info in info_lst:
                word = info.word
                translator = info.translator
                name = (word, translator)
                if name in source_word_translator_set:
                    continue
                source_word_translator_set.add(name)
                yield name

    # Source word node generator
    def source_nodes():
        for row in source_words_by_translator():
            source_word = row[0]
            translator = row[1]
            name = source_word + "-" + translator
            node = f"{metacode2lemma_map_src[source_word]} ({romaji2kanji_map[translator]})"
            node_type = 1
            type_label = "source"
            weight = 0
            info_lst = alignment_summary.query_details_by_source(row[0])
            for info in info_lst:
                if info.translator != row[1]:
                    continue
                weight += 1
            yield (name, node, node_type, type_label, weight)

    # Target word node generator
    def target_nodes():
        for word in target_words():
            name = word
            node = metacode2lemma_map_tar[word]
            node_type = 2
            type_label = "target"
            weight = 0
            info_lst = alignment_summary.query_details_by_target(word)
            for info in info_lst:
                weight += 1
                source_metacode = info.alignment[0].split("-")
                target_metacode = info.alignment[1].split("-")
                if source_metacode[:4] == target_metacode[:4]:
                    node_type = 3
                    type_label = "dublicate"
            yield (name, node, node_type, type_label, weight)

    # Igraph construction
    node_lst = list(source_nodes()) + list(target_nodes())
    edge_lst = list(edge_by_translator())
    graph = ig.Graph.TupleList(edge_lst, directed=False, edge_attrs=["weight"])

    for node_attr in node_lst:
        name, node, node_type, type_label, weight = node_attr
        for v in graph.vs:
            if v["name"] != name:
                continue
            v["node"] = node
            v["node_type"] = node_type
            v["type_label"] = type_label
            v["weight"] = weight

    return graph


def retrive_igraph_by_poem_by_translator(idx: str, *source_words):
    """Retrive igraph format data from one poem with a translator attension.

    :return graph: igraph-converted information.
    """
    target_word_set = set()
    source_word_translator_set = set()
    alignment_lst = DB.query_improper_alignment_by_word_in_poem(idx, *source_words)    
    alignment_lst = list(_filter(alignment_lst))
    alignment_summary = bitexts.AlignmentSummary(alignment_lst)
    edge_info = alignment_summary.alignment_info  # For edges" annotation

    # Edge by translator generator
    def edge_by_translator():
        for stat in alignment_summary.summary:
            source_word = stat.alignment[0]
            target_word = stat.alignment[1]
            stat = asdict(stat)
            for (key, value) in stat.items():
                if (key == "alignment") or (key == "total"):
                    continue
                source_node = f"{source_word}-{key}"
                target_node = target_word
                weight = value
                if weight == 0:
                    continue
                yield (source_node, target_node, weight)

    # Aligned target word generator
    def target_words():
        for info in edge_info:
            target_word = info.alignment[1]
            if target_word in target_word_set:
                continue
            target_word_set.add(target_word)
            yield target_word

    # Source word with translator coding generator
    def source_words_by_translator():
        for word in source_words:
            info_lst = alignment_summary.query_details_by_source(word)
            for info in info_lst:
                word = info.word
                translator = info.translator
                name = (word, translator)
                if name in source_word_translator_set:
                    continue
                source_word_translator_set.add(name)
                yield name

    # Source word node generator
    def source_nodes():
        for row in source_words_by_translator():
            source_word = row[0]
            translator = row[1]
            name = source_word + "-" + translator
            node = f"{metacode2lemma_map_src[source_word]} ({romaji2kanji_map[translator]})"
            node_type = 1
            type_label = "source"
            weight = 0
            info_lst = alignment_summary.query_details_by_source(row[0])
            for info in info_lst:
                if info.translator != row[1]:
                    continue
                weight += 1
            yield (name, node, node_type, type_label, weight)

    # Target word node generator
    def target_nodes():
        for word in target_words():
            name = word
            node = metacode2lemma_map_tar[word]
            node_type = 2
            type_label = "target"
            weight = 0
            info_lst = alignment_summary.query_details_by_target(word)
            for info in info_lst:
                weight += 1
                source_metacode = info.alignment[0].split("-")
                target_metacode = info.alignment[1].split("-")
                if source_metacode[:4] == target_metacode[:4]:
                    node_type = 3
                    type_label = "dublicate"
            yield (name, node, node_type, type_label, weight)

    # Igraph construction
    node_lst = list(source_nodes()) + list(target_nodes())
    edge_lst = list(edge_by_translator())
    graph = ig.Graph.TupleList(edge_lst, directed=False, edge_attrs=["weight"])

    for node_attr in node_lst:
        name, node, node_type, type_label, weight = node_attr
        for v in graph.vs:
            if v["name"] != name:
                continue
            v["node"] = node
            v["node_type"] = node_type
            v["type_label"] = type_label
            v["weight"] = weight

    return graph

