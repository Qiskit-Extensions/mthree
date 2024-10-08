import json
import time
import argparse

import mthree

import logging
logging.basicConfig(level=logging.INFO)

def main(distance=3):
    with open("data/eagle_large_counts.json") as json_file:
        counts = json.load(json_file)

    mit = mthree.M3Mitigation()
    mit.cals_from_file("data/eagle_large_cals.json")

    st = time.perf_counter()
    _ = mit.apply_correction(counts, range(127), distance=distance)
    fin = time.perf_counter()
    print(fin - st)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--distance', nargs='?', const=3, type=int)
    args = parser.parse_args()
    main(args.distance)
