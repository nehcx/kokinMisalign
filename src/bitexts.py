"""Bitext loader with query tools for search alignment information."""
from dataclasses import dataclass, field, asdict
from typing import List, Any
import argparse
from logging import basicConfig, getLogger, DEBUG
from utils import write_pickle
from methods import ibm2


@dataclass
class AlignmentInfo:
    """Alignment with information by a single target word."""

    word: str
    poem: str
    source_surface: str
    target_surface: str
    translator: str
    alignment: tuple


@dataclass
class AlignmentStat:
    """Word alignment information collective count statistics."""

    alignment: tuple
    total: int = field(default=0)
    kaneko: int = field(default=0)
    katagiri: int = field(default=0)
    kojimaarai: int = field(default=0)
    komachiya: int = field(default=0)
    kubota: int = field(default=0)
    kyusojin: int = field(default=0)
    matsuda: int = field(default=0)
    okumura: int = field(default=0)
    ozawa: int = field(default=0)
    takeoka: int = field(default=0)


@dataclass
class AlignmentSummary:
    """Word alignment information summary."""

    alignment_info: List[AlignmentInfo] = field(repr=False)
    summary: List[AlignmentStat] = field(init=False)

    def __post_init__(self):
        self.summary = list(self._summary())

    def _summary(self):
        alignment_dict = {}
        for info in self.alignment_info:
            alignment = info.alignment
            if alignment not in alignment_dict:
                alignment_dict[alignment] = asdict(AlignmentStat(alignment))
            alignment_dict[alignment]["total"] += 1
            alignment_dict[alignment][info.translator] += 1
        for stat in alignment_dict.values():
            yield AlignmentStat(**stat)

    def query_details_by_source(self, source):
        """Return alignment details (poems where the alignment appeared).

        Search by source for retrive hub nodes.
        :param source: str; source word.
        """
        for info in self.alignment_info:
            if info.alignment[0] != source:
                continue
            yield info

    def query_details_by_target(self, target):
        """Return alignment details (poems where the alignment appeared).

        Search by target for retrive periphery (translational word) nodes.
        :param target: str; target word.
        """
        for info in self.alignment_info:
            if info.alignment[1] != target:
                continue
            yield info

    def query_summary(self, alignment):
        """Return collective summary (by which translator).

        Search information summary by translators for edge annotation.
        :param alignment: tuple; source - target pair.
        """
        for stat in self.summary:
            if stat.alignment != alignment:
                continue
            yield stat


@dataclass
class Bitext:
    """Aligned bitext."""

    poem: str
    source: List[str] = field(init=False, repr=False)
    source_raw: str = field(repr=False)
    source_surface: str
    target: List[str] = field(init=False, repr=False)
    target_raw: str = field(repr=False)
    target_surface: str
    translator: str
    model_source2target: Any = field(repr=False)
    model_target2source: Any = field(repr=False)
    method: str = field(default="ibm2", repr=False)
    alignment_source2target: List[tuple] = field(init=False, repr=False)
    alignment_target2source: List[tuple] = field(init=False, repr=False)

    def __post_init__(self):
        self.source = self.source_raw.split("/")
        self.target = self.target_raw.split("/")
        self.alignment_source2target = list(self._alignment_src2tar())
        self.alignment_target2source = list(self._alignment_tar2src())

    def _alignment_src2tar(self):
        """Return aligment from source to target."""
        if self.method == "ibm2":
            return ibm2.aligned(source=self.source,
                                target=self.target,
                                model=self.model_source2target)
        # elif other alignment methods
        # ...

    def _alignment_tar2src(self):
        """Return aligment from source to target."""
        if self.method == "ibm2":
            return ibm2.aligned(source=self.target,
                                target=self.source,
                                model=self.model_target2source)
        # elif other alignment methods
        # ...

    def alignment_table_src2tar(self):
        """Return aligment table (pandas.DataFrame) from source to target."""
        if self.method == "ibm2":
            return ibm2.alignment_table(self.source, self.target,
                                        self.alignment_source2target,
                                        self.model_source2target)
        # elif other alignment methods
        # ...

    def alignment_table_tar2src(self):
        """Return aligment table (pandas.DataFrame) from target to source."""
        if self.method == "ibm2":
            return ibm2.alignment_table(self.target, self.source,
                                        self.alignment_target2source,
                                        self.model_target2source)
        # elif other alignment methods
        # ...

    def proper_alignment_idx(self):
        """Return proper aligned token index in both direction.

        :return: filter(List[tuple(int=src_idx,int=tar_idx)])
        """
        src2tar = self.alignment_source2target
        tar2src = self.alignment_target2source
        tar2src_inverse = [i[::-1] for i in tar2src]
        return filter(lambda x: x in tar2src_inverse, src2tar)

    def improper_alignment_idx(self):
        """Return aligned token index in only target-to-source direction.

        :return: filter(List[tuple(int=src_idx,int=tar_idx)])
        """
        src2tar = self.alignment_source2target
        tar2src = self.alignment_target2source
        tar2src_inverse = [i[::-1] for i in tar2src]
        proper_aligned = [i for i in src2tar if i in tar2src_inverse]
        return filter(lambda x: (x not in proper_aligned) & (None not in x),
                      tar2src_inverse)

    def proper_alignment(self):
        """Generate aligned token in both directions.

        :type: List[tuple(str=src_token,str=tar_token)]
        """
        for src_id, tar_id in self.proper_alignment_idx():
            yield (self.source[src_id], self.target[tar_id])

    def improper_alignment(self):
        """Generate proper_alignment token in both directions.

        :type: List[tuple(str=src_token,str=tar_token)]
        """
        for src_id, tar_id in self.improper_alignment_idx():
            yield (self.source[src_id], self.target[tar_id])

    def query_proper_alignment_by_token(self, token):
        """Return token"s alignment in both directions."""
        for alignment in self.proper_alignment():
            if alignment[0] != token:
                continue
            yield alignment

    def query_improper_alignment_by_token(self, token):
        """Return token"s alignment in only target-to-source directions."""
        for alignment in self.improper_alignment():
            if alignment[0] != token:
                continue
            yield alignment

    def sure_links(self):
        """Return sure links."""
        for i, src_token in enumerate(self.source):
            for j, tar_token in enumerate(self.target):
                if src_token[3:15] == tar_token[3:15]:
                    yield (i, j)

    def possible_links(self):
        """Return possible links."""
        for i, src_token in enumerate(self.source):
            for j, tar_token in enumerate(self.target):
                if src_token[3:9] == tar_token[3:9]:
                    yield (i, j)


@dataclass
class Bitexts:
    """Aligned bitexts."""

    translators: List[str] = field(default_factory=list)
    method: str = field(default="ibm2", repr=False)
    bitexts: List[Bitext] = field(init=False, repr=False)
    model_source2target: Any = field(init=False, repr=False)
    model_target2source: Any = field(init=False, repr=False)

    def __post_init__(self):
        self.model_source2target, self.model_target2source = self._load_models(
        )
        self.bitexts = list(self._read_bitexts())

    def __getitem__(self, index):
        return self.bitexts[index]

    def __iter__(self):
        for bitext in self.bitexts:
            yield bitext

    def _load_models(self):
        """Load model."""
        if self.method == "ibm2":
            return (ibm2.load("../model/ibm2_fwd.model"),
                    ibm2.load("../model/ibm2_bwd.model"))
        # elif other alignment methods
        # ...

    def _read_bitexts(self):
        with open("../cache/bitexts.csv") as fp:
            next(fp)
            for row in fp.readlines():
                fields = row.strip().split(",")
                if fields[-1] not in self.translators:
                    continue
                yield Bitext(*fields, self.model_source2target,
                             self.model_target2source, self.method)

    def query_bitext_by_word(self, *words):
        """Query bitext by words."""
        for bitext in self.bitexts:
            for word in words:
                if word not in bitext.source:
                    continue
                yield bitext

    def query_by_poem(self, idx: str):
        """Query bitext by words."""
        for bitext in self.bitexts:
            if idx != bitext.poem:
                continue
            yield bitext

    def query_bitext_by_translator(self, *translators):
        """Query bitext by translators."""
        for bitext in self.bitexts:
            for translator in translators:
                if translator != bitext.translator:
                    continue
                yield bitext

    def query_proper_alignment_by_word(self, *words):
        """Return proper alignment by words with full information."""
        bitexts_by_words = self.query_bitext_by_word(*words)
        for bitext in bitexts_by_words:
            for word in words:
                proper_alignment = bitext.query_proper_alignment_by_token(word)
                for alignment in proper_alignment:
                    yield AlignmentInfo(word, bitext.poem,
                                        bitext.source_surface,
                                        bitext.target_surface,
                                        bitext.translator, alignment)

    def query_improper_alignment_by_word(self, *words):
        """Return alignment only from translation-to-source words and info."""
        bitexts_by_words = self.query_bitext_by_word(*words)
        for bitext in bitexts_by_words:
            for word in words:
                improper_alignment = bitext.query_improper_alignment_by_token(
                    word)
                for alignment in improper_alignment:
                    yield AlignmentInfo(word, bitext.poem,
                                        bitext.source_surface,
                                        bitext.target_surface,
                                        bitext.translator, alignment)

    def query_improper_alignment_by_word_in_poem(self, idx: str, *words: str):
        """Return alignment only from translation-to-source words and info of one poem."""
        bitexts_by_words = self.query_bitext_by_word(*words)
        bitexts_by_words = [bitext for bitext in bitexts_by_words if bitext.poem == idx]
        for word in words:
            for bitext in bitexts_by_words:
                improper_alignment = bitext.query_improper_alignment_by_token(word)
                for alignment in improper_alignment:
                    yield AlignmentInfo(word, bitext.poem,
                                        bitext.source_surface,
                                        bitext.target_surface,
                                        bitext.translator, alignment)


def main(args):
    basicConfig(format="%(asctime)s %(message)s", level=DEBUG)
    logger = getLogger(__name__)
    logger.info(f"[INFO] args: {args}")
    logger.info("[INFO] Loading DB...")
    db = Bitexts(args.translators, args.method)
    logger.info("[INFO] Saving DB...")
    write_pickle(db, args.output_path)
    logger.info("[INFO] Done.")


def cli_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t",
                        "--translators",
                        nargs="+",
                        help="translators to include")
    parser.add_argument("-m",
                        "--method",
                        choices=["ibm2"],
                        help="selection of word alignment model")
    parser.add_argument("-o", "--output_path", help="path of output file")
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli_main()
