"""Train alignment models."""
import os
import argparse
from logging import basicConfig, getLogger, DEBUG
from utils import load_corpus, load_hyparam
from methods import ibm2  # and other methods

MODEL_PATH = "../model"
if not os.path.exists(MODEL_PATH):
    os.makedirs(MODEL_PATH)


def main(args):
    """Train and save alignment models."""
    basicConfig(format="%(asctime)s %(message)s", level=DEBUG)
    logger = getLogger(__name__)
    logger.info(f"[INFO] args: {args}")
    corpus = load_corpus(args.corpus_path)
    src = corpus.source
    tar = corpus.target
    if args.method == "ibm2":
        logger.info("[INFO] Training IBM model 2...")
        hyparams = load_hyparam("hyparam_ibm2.yaml")
        logger.info("[INFO] Training from source to target...")
        model_fwd = ibm2.train(source=src,
                               target=tar,
                               max_iter=hyparams.iterations)
        logger.info("[INFO] Training from target to source...")
        model_bwd = ibm2.train(source=tar,
                               target=src,
                               max_iter=hyparams.iterations)
        fp_fwd = os.path.join(MODEL_PATH, args.fn_fwd)
        fp_bwd = os.path.join(MODEL_PATH, args.fn_bwd)
        logger.info(f"[INFO] Saving models to {MODEL_PATH}...")
        ibm2.save(fp_fwd, model_fwd)
        ibm2.save(fp_bwd, model_bwd)
        logger.info("[INFO] Done.")


def cli_main():
    """Arguement parser setting."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--fn_bwd", help="path of output forward model")
    parser.add_argument("-c", "--corpus_path", help="path of bitexts")
    parser.add_argument("-f", "--fn_fwd", help="path of output backward model")
    parser.add_argument("-m",
                        "--method",
                        choices=["ibm2"],
                        help="selection of word alignment model")
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli_main()
