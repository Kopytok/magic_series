import logging
from functools import reduce

def nanCnt(lst):
    return len([x for x in lst if x == -1])

def rowSum(lst):
    return sum(int(x) for x in lst if x > -1)

def pruneLastMissingNumber(domain):
    """ Fill in last missing number """
    numbers = domain.toDigits()
    if nanCnt(numbers) == 1:
        last_value = len(domain) - rowSum(numbers)
        if last_value < len(numbers):
            domain[numbers.index(-1)] = last_value

def pruneSumEqLen(domain):
    """ Check """
    length = len(domain)
    out = domain.copy()
    for value, row in enumerate(out.grid):
        for position, it in enumerate(row):
            if it == -1:
                min_eval = out.eval(value, position, how='min')
                max_eval = out.eval(value, position, how='max')

                constraints = [
                    sum(min_eval) > length,
                    sum(max_eval) < length,
                    sum([t * n for t, n in enumerate(min_eval)]) > length,
                    sum([t * n for t, n in enumerate(max_eval)]) < length,
                ]

                if reduce(lambda x, y: x or y, constraints):
                    domain.grid[value, position] = 0

def pruneLessThanCurSum(domain):
    numbers = domain.toDigits()
    for num in numbers:
        if num > -1:
            num_cnt = [x for x in numbers if x == num]
            for value, position in enumerate(num_cnt):
                if domain.grid[value, position] == -1:
                    domain.grid[value, position] = 0

def pruneKnownRowSum(domain):
    numbers = domain.toDigits()
    for position, value in enumerate(numbers):
        if value > -1 and domain.rowSum(position) == value:
            domain.grid[position, :] = \
                [x if x > -1 else 0 for x in domain.grid[position, :]]

def pruneFillColumn(domain):
    temp = domain.copy()
    for position, col in enumerate(temp.grid.T):
        # Fill the last missing value within column
        if domain.nanCnt(position) == 1:
            col = [x if x > -1 else 1 - domain.rowSum(position) for x in col]
        # Fill with '0' if there's already 1 in column
        if domain.rowSum(position) == 1:
            col = [0 if x != 1 else 1 for x in col]
        domain.grid[:, position] = col.copy()

def pruneSumReady(domain):
    for value, row in enumerate(domain.grid):
        if -1 not in row and sum(row) < len(row):
            domain[value] = int(sum(row))

def prune(domain):
    pruned = domain.copy()
    constraints = [
        "pruneFillColumn",
        "pruneSumEqLen",
        "pruneLastMissingNumber",
        "pruneLessThanCurSum",
        "pruneKnownRowSum",
        "pruneSumReady",
    ]
    for func in constraints:
        eval("%s(pruned)" % func)
        logging.debug("After {}:\n{}".format(func, repr(domain)))
    return pruned
