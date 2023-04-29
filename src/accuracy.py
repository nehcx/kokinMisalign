"""Calculate accuracy.

Sure links and possible links are defined by matching rate of metacodes.
"""
import csv
from logging import basicConfig, getLogger, DEBUG
from utils import load_pickle

basicConfig(format="%(asctime)s %(message)s", level=DEBUG)
logger = getLogger(__name__)

logger.info("[INFO] Loading...")

DB = load_pickle("../cache/bitexts.db")

total_A_and_P_src2tar = 0
total_A_and_S_src2tar = 0
total_A_src2tar = 0
total_S_src2tar = 0

total_A_and_P_tar2src = 0
total_A_and_S_tar2src = 0
total_A_tar2src = 0
total_S_tar2src = 0

total_A_and_P_bidirection = 0
total_A_and_S_bidirection = 0
total_A_bidirection = 0
total_S_bidirection = 0

# Count total alignment number, sure link number, possible link number
for bitext in DB:
    A_src2tar = set(bitext.alignment_source2target)
    A_tar2src = set(bitext.alignment_target2source)
    A_bidirection = set(bitext.proper_alignment_idx())  # bidirection alignment == proper alignment
    S_src2tar = set(bitext.sure_links())
    S_tar2src = set([a[::-1] for a in bitext.sure_links()])
    S_bidirection = set(bitext.sure_links())  # same direction as src2tar
    P_src2tar = set(bitext.possible_links())
    P_tar2src = set([a[::-1] for a in bitext.possible_links()]) 
    P_bidirection = set(bitext.possible_links())  # same direction as src2tar

    n_A_and_P_src2tar = len(A_src2tar.intersection(P_src2tar))
    n_A_and_S_src2tar = len(A_src2tar.intersection(S_src2tar))
    n_A_src2tar = len(A_src2tar)
    n_S_src2tar = len(S_src2tar)

    n_A_and_P_tar2src = len(A_tar2src.intersection(P_tar2src))
    n_A_and_S_tar2src = len(A_tar2src.intersection(S_tar2src))
    n_A_tar2src = len(A_tar2src)
    n_S_tar2src = len(S_tar2src)

    n_A_and_P_bidirection = len(A_bidirection.intersection(P_bidirection))
    n_A_and_S_bidirection = len(A_bidirection.intersection(S_bidirection))
    n_A_bidirection = len(A_bidirection)
    n_S_bidirection = len(S_bidirection)

    total_A_and_P_src2tar += n_A_and_P_src2tar
    total_A_and_S_src2tar += n_A_and_S_src2tar
    total_A_src2tar += n_A_src2tar
    total_S_src2tar += n_S_src2tar

    total_A_and_P_tar2src += n_A_and_P_tar2src
    total_A_and_S_tar2src += n_A_and_S_tar2src
    total_A_tar2src += n_A_tar2src
    total_S_tar2src += n_S_tar2src

    total_A_and_P_bidirection += n_A_and_P_bidirection
    total_A_and_S_bidirection += n_A_and_S_bidirection
    total_A_bidirection += n_A_bidirection
    total_S_bidirection += n_S_bidirection


def calc(A, S, AP, AS):
    """Return precision, recall, AER."""
    precision = AP / A
    recall = AS / S
    AER = 1 - (AP + AS) / (A + S)
    return precision, recall, AER


logger.info("[Info] Calculating precision, recall and AER...")

source2target = {}
target2source = {}
bidirection = {}
source2target["precision"], source2target["recall"], source2target[
    "AER"] = calc(total_A_src2tar, total_S_src2tar,
                  total_A_and_P_src2tar, total_A_and_S_src2tar)
target2source["precision"], target2source["recall"], target2source[
    "AER"] = calc(total_A_tar2src, total_S_tar2src,
                  total_A_and_P_tar2src, total_A_and_S_tar2src)
bidirection["precision"], bidirection["recall"], bidirection["AER"] = calc(
    total_A_bidirection, total_S_bidirection, total_A_and_P_bidirection,
    total_A_and_S_bidirection)
res = source2target, target2source, bidirection

with open("../artifacts/accuracy.csv", 'w') as fp:
    writer = csv.writer(fp, delimiter=",")
    writer.writerow(
        ["model", "source → target", "target → source", "bidirection"])
    for key in bidirection.keys():
        writer.writerow([key] + [f"{d[key]*100:3.2f}" for d in res])

logger.info("[Info] Done.")
