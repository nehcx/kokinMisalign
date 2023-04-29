"""Statistical description of the data."""
import csv
from logging import basicConfig, getLogger, DEBUG
from utils import load_pickle

basicConfig(format="%(asctime)s %(message)s", level=DEBUG)
logger = getLogger(__name__)

logger.info("[INFO] Loading...")

DB = load_pickle("../cache/bitexts.db")

n_bitext = {}
n_bitext["total"] = 0
source_token_lst = []
target_token_dict = {}
target_token_dict["total"] = []
for translator in DB.translators:
    bitext_lst = list(DB.query_bitext_by_translator(translator))
    n_bitext[translator] = len(bitext_lst)
    n_bitext["total"] += len(bitext_lst)
    target_token_dict[translator] = []
    for bitext in bitext_lst:
        source = bitext.source
        target = bitext.target
        for token in source:
            source_token_lst.append(token)
        for token in target:
            target_token_dict[translator].append(token)
            target_token_dict["total"].append(token)

n_source_token = len(source_token_lst)
n_source_type = len(set(source_token_lst))

n_token = {}
n_type = {}
for key in target_token_dict:
    n_token[key] = len(target_token_dict[key])
    n_type[key] = len(set(target_token_dict[key]))

n_token["kokin"] = n_source_token
n_type["kokin"] = n_source_type
n_bitext["kokin"] = n_bitext["total"] / len(DB.translators)
res = n_token, n_type, n_bitext

with open("../artifacts/basic_stat.csv", 'w') as fp:
    writer = csv.writer(fp, delimiter=",")
    writer.writerow(["", "# of tokens", "# of types", "# of texts"])
    for key in n_token.keys():
        writer.writerow([key] + [f"{int(d[key])}" for d in res])

logger.info("[Info] Done.")
