import os
import time
import logging

import numpy as np

from solver.domain import MISSING_CHAR, Domain

logging_path = os.path.join(os.getcwd(), "text_log.log")

logging.basicConfig(level=logging.DEBUG,
    format="%(levelname)s - %(asctime)s - %(msg)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(logging_path),
        logging.StreamHandler(),
    ])

def search(domain):
    temp = domain.copy()

    # Feasibility testing & pruning
    logging.debug("Before pruning:\n{}".format(repr(temp)))
    while temp.feasibilityCheck():
        tmp = temp.prune()
        if np.array_equal(temp.grid, tmp.grid):
            break
        else:
            temp = tmp.copy()
    if not temp.feasibilityCheck():
        return False
    if MISSING_CHAR not in str(temp):
        return set([str(temp)])
    logging.debug("After pruning:\n{}".format(repr(temp)))

    # Making a guess
    answers = set()
    for value, position in temp:
        logging.debug("Try value {} in position {}".format(value, position))
        temp_sum = temp.copy()
        temp_sum[position] = value
        out = search(temp_sum)
        if isinstance(out, set):
            answers |= out
    return answers

def solve(domain):
    t0 = time.time()
    answer = search(domain)
    if answer:
        logging.info("Length {}: {}".format(len(domain), answer))
    else:
        logging.info("No magic series of length %d" % len(domain))
    logging.info("Solved in %02d:%02d\n" % divmod(time.time() - t0, 60))
    return answer

def main(length):
    d = Domain(length)
    return solve(d)

if __name__ == "__main__":
    main(5)
