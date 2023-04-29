"""Train model using IBM 2 model with nltk."""
import dill as pickle
from pandas import DataFrame
from nltk.translate import AlignedSent, IBMModel2


def bitext(source: str, target: str, sep: str = "/"):
    """Return AlignedSent."""
    return AlignedSent(words=source.split(sep), mots=target.split(sep))


def corpus(source: iter, target: iter, sep: str = "/"):
    """Build aligned corpus for IBM Model 2 from two iterable objects."""
    return list(map(lambda x: bitext(x[0], x[1], sep), zip(source, target)))


def train(source: iter, target: iter, max_iter: int, sep="/"):
    """Train IBM 2 alignment model.

    Source and target should be iterable object of comma-delimitated strings.
    """
    aligned_corpus = corpus(source, target, sep)
    return IBMModel2(aligned_corpus, max_iter)


def save(fname, model):
    """Output model as pickle."""
    fp = open(fname, "wb")
    pickle.dump(model, fp)


def load(fname):
    """Load model."""
    fp = open(fname, "rb")
    return pickle.load(fp)


def aligned(source: list, target: list, model):
    """Return aligned bitext."""
    l = len(target)
    m = len(source)
    for j, tar_token in enumerate(source):
        # Initialize tar_token to align with the NULL token
        best_prob = (model.translation_table[tar_token][None] *
                     model.alignment_table[0][j + 1][l][m])
        best_prob = max(best_prob, model.MIN_PROB)
        best_alignment_point = None
        for i, src_token in enumerate(target):
            align_prob = (model.translation_table[tar_token][src_token] *
                          model.alignment_table[i + 1][j + 1][l][m])
            if align_prob >= best_prob:
                best_prob = align_prob
                best_alignment_point = i
        yield (j, best_alignment_point)


# def alignment(aligned_sent: AlignedSent):
# """Return alignments List[Tuple(int,int)]."""
# return sorted(list(aligned_sent.alignment))
# def id2str():
#     for src_id, tar_id in aligned_sent.alignment:
#         yield (aligned_sent.words[src_id], aligned_sent.mots[tar_id])

# return list(id2str())


def alignment_table(source, target, alignment, model):
    """Return alignment table with details."""
    len_src = len(source)
    len_tar = len(target)

    def details():
        for src_id, tar_id in alignment:
            token_src = source[src_id]
            if tar_id is not None:
                token_tar = target[tar_id]
            else:
                token_tar = "NULL"
            translate_prob = model.translation_table[token_src][token_tar]
            alignment_prob = model.alignment_table[src_id][tar_id][len_src][
                len_tar]
            yield (src_id, tar_id, token_src, token_tar, translate_prob,
                   alignment_prob)

    alignment_dict = {}
    alignment_dict["source_token_id"], alignment_dict[
        "target_token_id"], alignment_dict["source_token"], alignment_dict[
            "target_token"], alignment_dict[
                "translate_probability"], alignment_dict[
                    "alignment_probability"] = map(list, list(zip(*details())))

    alignment_df = DataFrame.from_dict(alignment_dict,
                                       orient="index").transpose()
    alignment_df = alignment_df.sort_values(by="source_token_id",
                                            ignore_index=True)
    alignment_df["probability"] = alignment_df[
        "translate_probability"] * alignment_df["alignment_probability"]
    alignment_df["normalized_probability"] = (
        alignment_df["probability"] - alignment_df["probability"].mean()
    ) / alignment_df["probability"].std(ddof=0)

    return alignment_df
