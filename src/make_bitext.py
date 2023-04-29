"""Use Konkinwakashu and translations to construct bitexts."""
import argparse
from logging import basicConfig, getLogger, DEBUG
import re
import pandas as pd

translator_lst = [
    'kaneko', 'katagiri', 'kojimaarai', 'komachiya', 'kubota', 'kyusojin',
    'matsuda', 'okumura', 'ozawa', 'takeoka'
]


def _idx2str(corpus, poem_idx):
    """Obtain poem string from corpus.

    :param corpus: pandas.DataFrame; vocabulary database
    :param poem_idx: str; poem index
    :param corpus_type: str: target or source

    :return bg_id: str; BunruiGoiShu id string
    :return surface: str; surface form string
    """
    token = corpus[corpus.poem_id.str.match(poem_idx)]
    surface = "".join(map(str, token.surface))
    # Keep noun (no include pronoun), verb (no include passive), 
    # adv (no include ない), adj (no include ない), and proper name;
    # pattern = re.compile(r'BG-16|BG-0[456789]|BG-03-1000|BG-03-1200-02|BG-03-1400-04-200-A|BG-03-1300-01|BG-02-1110|BG-01-1[07]00|BG-01-1010')  
    bg_id = "/".join(filter(lambda x: "BG-16" not in x, token.bg_id))
    return bg_id, surface


def load_kokin(fname):
    """Load source (Kokinwakashu original texts)."""
    logger = getLogger(__name__)
    logger.info(f"[INFO] Loading {fname} for Kokinwakashu texts...")
    hachidai = pd.read_table(fname,
                             usecols=range(9),
                             sep=" ",
                             names=[
                                 "idx", "token_type", "bg_id", "chasen_id",
                                 "surface", "lemma", "lemma_reading", "kanji",
                                 "kanji_reading"
                             ])
    hachidai["anthology_id"] = hachidai.idx.map(lambda x: x.split(":")[0])
    hachidai["poem_id"] = hachidai.idx.map(lambda x: x.split(":")[1])
    hachidai["token_id"] = hachidai.idx.map(lambda x: x.split(":")[2])
    hachidai["general_id"] = hachidai.bg_id.map(lambda x: x.split("-")[0])
    hachidai["pos_id"] = hachidai.bg_id.map(lambda x: x.split("-")[1])
    hachidai["group_id"] = hachidai.bg_id.map(lambda x: x.split("-")[2])
    hachidai["filed_id"] = hachidai.bg_id.map(lambda x: x.split("-")[3])
    hachidai["exact_id"] = hachidai.bg_id.map(lambda x: x.split("-")[4])
    kokin_voc = hachidai[(
        hachidai.token_type.str.match("A00")
        |  # simplex without variant complex
        hachidai.token_type.str.match("B00") |  # complex
        hachidai.token_type.str.match("D00")  # proper noun complex
    ) & hachidai.anthology_id.str.match("01")  # only kokinshu
                         ]
    kokin = pd.DataFrame()
    kokin["idx"] = kokin_voc.poem_id.unique()
    kokin["source"], kokin["src_surface"] = tuple(
        zip(*kokin.idx.map(lambda x: _idx2str(kokin_voc, x))))
    kokin["idx"] = kokin.idx.map(int)
    return kokin


def load_translation(fname, translator):
    """Load target (translations of Kokinwakashu)."""
    logger = getLogger(__name__)
    logger.info(f"[INFO] Loading {fname} for {translator}'s traslation...")
    target_voc = pd.read_table(fname,
                               usecols=range(11),
                               sep=" ",
                               names=[
                                   "variant", "translator", "poem_id",
                                   "variant_id", "a", "b", "c", "bg_id",
                                   "surface", "reading", "lemma"
                               ],
                               dtype={
                                   "variant": "string",
                                   "poem_id": "string",
                                   "variant_id": "string",
                               })
    target_voc_by_translator = target_voc[target_voc.translator ==
                                          translator]  # select translator
    target_voc_by_translator = target_voc_by_translator[(
        (target_voc_by_translator.variant_id == "1") |
        (target_voc_by_translator.variant_id == "0")
    )  # exclude infeasible variant
                                                        ]
    target_by_translator = pd.DataFrame()
    target_by_translator["idx"] = target_voc_by_translator.poem_id.unique()
    target_by_translator["target"], target_by_translator[
        "tar_surface"] = tuple(
            zip(*target_by_translator.idx.map(
                lambda x: _idx2str(target_voc_by_translator, x))))
    target_by_translator["translator"] = translator
    target_by_translator["idx"] = target_by_translator.idx.map(int)
    return target_by_translator


def _make_bitext(source_df, target_df):
    """Make source-target bitexts.

    :param source_df: pandas.DataFrame; kokinshu strings
    :param target_df: pandas.DataFrame; translation strings

    :return bitext_df: pandas.DataFrame; bitexts data frame
    """
    bitext_df = pd.merge(source_df, target_df)
    return bitext_df


def _make_bitext_by_translator(fname, source_df, tanslator):
    """Make by-translator source-target bitexts."""
    return _make_bitext(
        source_df,
        load_translation(fname, tanslator).sort_values(by="idx",
                                                       ignore_index=True))


def main(args):
    """Concat by-translator bitexts."""
    basicConfig(format="%(asctime)s %(message)s", level=DEBUG)
    logger = getLogger(__name__)
    logger.info(f"[INFO] args: {args}")
    source_df = load_kokin(args.src_path).sort_values(by="idx",
                                                      ignore_index=True)
    translators = translator_lst
    bitext_lst = list(
        map(
            lambda translator: _make_bitext_by_translator(
                args.tar_path, source_df, translator), translators))
    logger.info("[INFO] Concating bitexts...")
    all_bitext = pd.concat(bitext_lst, axis=0, ignore_index=True)
    all_bitext.to_csv(args.out_path, index=False)
    logger.info("[INFO] Made bitexts.")


def cli_main():
    """Parser arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--src_path", help="path of source DB")
    parser.add_argument("-t", "--tar_path", help="path of target DB")
    parser.add_argument("-o", "--out_path", help="path of output file")
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli_main()
