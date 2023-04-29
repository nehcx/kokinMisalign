"""Make metacode to lemma mapping dictionary."""
import re
import argparse
from logging import basicConfig, getLogger, DEBUG
from utils import write_pickle


def main(args):
    """Make metacode to lemma mapping dictionary."""
    basicConfig(format="%(asctime)s %(message)s", level=DEBUG)
    logger = getLogger(__name__)
    logger.info(f"[INFO] args: {args}")
    map_dict = {"NULL": "NULL"}
    with open(args.file_path) as fp:
        for line in fp:
            try:
                if args.db_format == "source":
                    if line[:2] != "01":
                        continue
                    decomp = line.split()[1]
                    if (decomp[0] == "C") | (decomp[0] == "E"):
                        continue
                    metacode = re.search(r'(BG|CH|PR|JO)-.{2}-.{4}-.{2}-.{4}',
                                         line).group()
                elif args.db_format == "target":
                    metacode = re.search(
                        r'(BG|CH|PR|JO)-.{2}-.{4}-.{2}-.{3}-.', line).group()
                else:
                    continue
            except AttributeError:
                logger.debug("[Debug] No metacode at '{}' in {} texts.".format(
                    line.strip(), args.db_format))
                metacode = None
            if metacode:
                if metacode not in map_dict.keys():
                    if args.db_format == "source":
                        lemma = line.strip().split()[5]
                        map_dict[metacode] = lemma
                    elif args.db_format == "target":
                        lemma = line.strip().split()[-1]
                        map_dict[metacode] = lemma
                    else:
                        continue
    logger.info(f"[INFO] Saving {args.output_path}...")
    write_pickle(map_dict, args.output_path)
    logger.info("[INFO] Done.")


def cli_main():
    """Arguement parser setting."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file_path", help="path of vocabulary dataset")
    parser.add_argument("-o", "--output_path", help="path of output file")
    parser.add_argument("-t",
                        "--db_format",
                        choices=["source", "target"],
                        help="input database format: source/target")
    args = parser.parse_args()
    main(args)


if __name__ == "__main__":
    cli_main()
