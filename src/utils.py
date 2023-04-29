"""Input / output utils."""
import dill as pickle
import pandas as pd
from hydra import initialize, compose


def write_pickle(data, fname):
    """Output data as .pkl."""
    fp = open(fname, "wb")
    pickle.dump(data, fp)


def load_pickle(fname):
    """Load .pkl files."""
    fp = open(fname, "rb")
    return pickle.load(fp)


def load_corpus(fname):
    """Load .csv corpus file."""
    return pd.read_csv(fname)


def metacode2lemma_map(fp_dict, metacode):
    """Convert metacode to lemma."""
    converter = load_pickle(fp_dict)
    return converter[metacode]


def load_hyparam(fname, fp_config="../params"):
    """Load model's hyperparameters."""
    with initialize(version_base=None, config_path=fp_config, job_name=None):
        hyparam = compose(config_name=fname)
    return hyparam


def lemma2metacode(word, metacode2lemma_map):
    """Convert lemma to bg-id format to query."""
    def metacodes():
        for key, value in metacode2lemma_map.items():
            if word != value:
                continue
            yield key

    metacode_lst = list(metacodes())
    if len(metacode_lst) == 1:
        return metacode_lst[0]
    elif len(metacode_lst) >= 2:
        print("Lemma has the following semantic codings:")
        multi_choice = {}
        for idx, metacode in enumerate(metacode_lst, 1):
            print(f"{idx:2d}: {metacode}")
            multi_choice[idx] = metacode
        choice = int(input("Input one ID to query:"))
        return multi_choice[choice]
