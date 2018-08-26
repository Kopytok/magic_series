import os
import time
import logging
import datetime

import numpy as np
import pandas as pd

from solver.domain import MISSING_CHAR, Domain

logging_path = os.path.join(os.getcwd(), "text_log.log")

logging.basicConfig(level=logging.INFO,
    format="%(levelname)s - %(asctime)s - %(msg)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(logging_path), # For debug
        logging.StreamHandler(),
    ])

def save_perfomance(length, seconds, commit_id=""):
    perfomance_path = "perfomance.csv"
    try:
        perfomance = pd.read_csv(perfomance_path)
    except FileNotFoundError as e:
        perfomance = pd.DataFrame(
            columns=["history_dt",  "length", "execution_tm"])
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    perfomance = perfomance.append([{
        "history_dt":   now,
        "length":       length,
        "execution_tm": seconds,
    }])
    perfomance.to_csv(perfomance_path, index=False)
    return

def search(domain):
    temp_domain = domain.copy()
    # Feasibility test & pruning
    logging.debug("Before pruning:\n{}".format(repr(temp_domain)))
    feasible = temp_domain.prune()
    if not feasible:
        logging.debug("Not feasible")
        return None
    logging.debug("After pruning:\n{}".format(repr(temp_domain)))
    if MISSING_CHAR not in str(temp_domain):
        return set([str(temp_domain)])

    # Make a guess
    answers = set()
    for value, position in temp_domain:
        logging.debug("Try value {} in position {}".format(value, position))
        temp_sum = temp_domain.copy()
        temp_sum[position] = value
        result = search(temp_sum)
        if result:
            answers |= result
    return answers

def solve(domain):
    t0 = time.time()
    answer = search(domain)
    if answer:
        logging.info("Length {}: {}".format(len(domain), answer))
    else:
        logging.info("No magic series found for length %d" % len(domain))
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
    for length in range(3,30):
        logging.info("Length %d" % length)
        domain = Domain(length)
        _, execution_time = solve(domain)
        save_perfomance(length, execution_time)

if __name__ == "__main__":
    # main()
    test()
