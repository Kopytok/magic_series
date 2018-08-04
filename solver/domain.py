import logging
from itertools import product

import numpy as np

from .prune import nanCnt, rowSum, prune

MISSING_CHAR = b'\xc2\xb7'.decode('utf8')

class Domain(object):
    def __init__(self, length):
        self.grid = np.array([[-1] * length] * length)

    def __repr__(self):
        rows = list()
        for row in self.grid:
            rows.append("".join(str(it) if it > -1 else MISSING_CHAR
                        for it in row))
        return "\n".join(rows)

    def __str__(self):
        digits = list()
        for col in self.grid.T:
            if sum(col) == 1:
                digits.append(str(np.where(col == 1)[0][0]))
            else:
                digits.append(MISSING_CHAR)
        return "".join(digits)

    def __getitem__(self, number):
        col = list()
        for row in self.grid:
            col.append(row[number])
        return col

    def __setitem__(self, position, number):
        new_grid = list()
        for i, row in enumerate(self.grid):
            new_col = list()
            for index, it in enumerate(row):
                if index == position:
                    new_col.append(int(i == number))
                else:
                    new_col.append(it)
            new_grid.append(new_col)
        self.grid = np.array([row[:] for row in new_grid])

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

    def toDigits(self):
        """ Convert domain into digits """
        digits = list()
        for col in self.grid.T:
            if sum(col) == 1:
                digits.append(np.where(col == 1)[0][0])
            else:
                digits.append(-1)
        return digits

    def rowSum(self, row):
        """ Sum of elements in row `row` """
        return rowSum(self.grid[row])

    def nanCnt(self, row):
        """ Count unresolved items in row """
        return nanCnt(self.grid[row])

    def feasibilityCheck(self):
        """ Test if domain is feasible """
        rng = range(len(self))
        for value, position in product(rng, rng):
            it = self.grid[value, position]
            if it > -1:
                row_sum = self.rowSum(position)
                nan_cnt = self.nanCnt(position)
                try:
                    available = range(row_sum, row_sum + nan_cnt + 1)
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
