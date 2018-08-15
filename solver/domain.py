import logging
from itertools import product

import numpy as np

from .prune import nan_cnt, row_sum, prune

MISSING_CHAR = b'\xc2\xb7'.decode('utf8')

class Domain(object):
    def __init__(self, length):
        self.grid = -np.ones((length, length))
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
        empty_cnt = dict()
        for position, col in enumerate(self.grid.T):
            if sum(col) < 1:
                empty_cnt[position] = len([x for x in col if x == -1])

        for position in sorted(empty_cnt, key=empty_cnt.get):
            empty_value = np.where(self.grid[:, position] == -1)[0][::-1]
            for value in empty_value:
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
        digits = list()
        for col in self.grid.T:
            if sum(col) == 1:
                digits.append(np.where(col == 1)[0][0])
            else:
                digits.append(-1)
        return digits

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
                row_sum_1 = self.row_sum(position)
                nan_cnt_1 = self.nan_cnt(position)
                try:
                    available = range(row_sum_1, row_sum_1 + nan_cnt_1 + 1)
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
