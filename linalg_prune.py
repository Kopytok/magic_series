from functools import reduce
import logging

import numpy as np

def prune_sum_eq_len(domain):
    constraints = [
        domain.estimate("min") > domain.length,
        domain.estimate("max") < domain.length,
    ]
    pad = reduce(lambda x, y: x | y, constraints)
    pad = pad & np.isnan(domain.grid)
    domain.grid = np.where(pad, ~pad, domain.grid)
    return pad.any()

def prune_fill_last_col(domain):
    """ Fill with 1 if last available position in column """
    pad = np.isnan(domain.grid) * (np.isnan(domain.grid).sum(0) == 1)
    domain.grid = np.where(pad, pad, domain.grid)
    return pad.any()

def prune(domain):
    """ Prune using listed functions """
    logging.debug("Input domain:\n%s" % str(domain))
    constraints = [
        prune_sum_eq_len,
        prune_fill_last_col,
    ]
    changed = feasible = True
    while changed and feasible:
        changed = any([func(domain) for func in constraints])
        feasible = domain.feasibility_test().all()
        logging.debug("Feasible: {}".format(feasible))
    return feasible
