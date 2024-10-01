import json
import time

import mthree


def main():
    with open('data/eagle_large_counts.json') as json_file:
        counts = json.load(json_file)

    mit = mthree.M3Mitigation()
    mit.cals_from_file('data/eagle_large_cals.json')

    st = time.perf_counter()
    quasi = mit.apply_correction(counts, range(127), distance=3)
    fin = time.perf_counter()
    print(fin-st)


if __name__ == "__main__":
    main()
