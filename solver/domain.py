import logging
from itertools import product

import numpy as np

from .prune import nan_cnt, row_sum, prune

MISSING_CHAR = b'\xc2\xb7'.decode('utf8')

class Domain(object):
    def __init__(self, length):
        self.grid = -np.ones((length, length))
        self.grid[0, 0] = 0
        self.length = length

    def __repr__(self):
        return "\n".join(["".join(str(int(it)) if it > -1 else MISSING_CHAR
                          for it in row) for row in self.grid])

    def __str__(self):
        return "".join([str(np.where(col == 1)[0][0]) if sum(col == 1)
                        else MISSING_CHAR for col in self.grid.T])

    def __getitem__(self, number):
        return [row[number] for row in self.grid]

    def __setitem__(self, position, number):
        self.grid = np.array([[int(i == number) if index == position else it
                    for index, it in enumerate(row)]
                    for i, row in enumerate(self.grid)])

    def __len__(self):
        return self.grid.shape[0]

    def __iter__(self):

        nan_per_col = dict()
        for position, col in enumerate(self.grid.T):
            if sum(col) < 1:
                nan_per_col[position] = nan_cnt(col)

        position = min(nan_per_col, key=nan_per_col.get)
        iter_col = self.grid.T[position]
        empty_positions = np.where(iter_col == -1)[0][::-1]
        for value in empty_positions:
            yield value, position

    def eval(self, value, position, how='min'):
        """ Evaluate max or min possible solution
            if `value` placed in `position` """
        logging.debug("Eval. Current solution %s" % str(self))
        eval_numbers = list()
        for n, col in enumerate(self.grid.T):
            if 1 in col and n != position:
                eval_numbers.append(np.where(col == 1)[0][0])
            elif n == position:
                eval_numbers.append(value)
            else:
                missing = np.where(col == -1)[0]
                logging.debug("Eval. n: {}\tcol: {}\tmissing: {}"
                              .format(n, col, missing))
                eval_numbers.append(missing[{'min': 0, 'max': -1}[how]])
        return eval_numbers

    def copy(self):
        """ Make copy of Domain """
        new_domain = Domain(len(self))
        new_domain.grid = np.copy(self.grid)
        return new_domain

    def to_digits(self):
        """ Convert domain into digits """
        return [np.where(col == 1)[0][0] if sum(col) == 1 else -1
                for col in self.grid.T]

    def row_sum(self, row):
        """ Sum of elements in row `row` """
        return row_sum(self.grid[row])

    def nan_cnt(self, row):
        """ Count unresolved items in row """
        return nan_cnt(self.grid[row])

    def feasibility_test(self):
        """ Test if domain is feasible """
        rng = range(len(self))
        for value, position in product(rng, rng):
            it = self.grid[value, position]
            if it > -1:
                rowSum = self.row_sum(position)
                nanCnt = self.nan_cnt(position)
                try:
                    available = range(rowSum, rowSum + nanCnt + 1)
                    left_values = [x for x in available if x != value]
                    assert (it == 1 and value in list(available)) or \
                           (it == 0 and len(left_values))
                except AssertionError as e:
                    return False
        return True

    def prune(self):
        return prune(self)

if __name__ == "__main__":
    pass
