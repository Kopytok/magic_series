import os
import time
import logging

import numpy as np
import pandas as pd

from solver.domain import MISSING_CHAR, Domain

logging_path = os.path.join(os.getcwd(), "text_log.log")

logging.basicConfig(level=logging.INFO,
    format="%(levelname)s - %(asctime)s - %(msg)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        # logging.FileHandler(logging_path), # For debug
        logging.StreamHandler(),
    ])

def save_perfomance(length, seconds, commit_id=""):
    import datetime

    perfomance_path = "perfomance.csv"
    try:
        perfomance = pd.read_csv(perfomance_path)
    except FileNotFoundError as e:
        perfomance = pd.DataFrame(
            columns=["history_dt", "commit_id",  "length", "execution_tm"])
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    perfomance = perfomance.append([{
        "history_dt":   now,
        "commit_id":    commit_id,
        "length":       length,
        "execution_tm": seconds,
    }])
    perfomance.to_csv(perfomance_path, index=False)
    return

def search(domain):
    temp = domain.copy()
    # Feasibility testing & pruning
    logging.debug("Before pruning:\n{}".format(repr(temp)))
    temp = temp.prune()
    if not temp.feasibility_test():
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
    return answer, time.time() - t0

def main():
    while True:
        try:
            length = int(input("Input series length as positive integer: "))
            assert length > 0
            break
        except (ValueError, AssertionError) as e:
            print("Wrong input. Write positive integer")
            continue

    domain = Domain(length)
    answer, execution_time = solve(domain)
    save_perfomance(length, execution_time)
    return answer

def test():
    git_commit = input("Input git commit id: ")
    for length in range(4, 10):
        logging.info("Started length %d" % length)
        for i in range(1):
            logging.info("Run #%d" % i)
            domain = Domain(length)
            _, execution_time = solve(domain)
            save_perfomance(length, execution_time, git_commit)

if __name__ == "__main__":
    # main()
    test()
