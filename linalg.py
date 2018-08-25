import os
import copy
import logging
import time

import numpy as np

from linalg_prune import prune

logging_path = os.path.join(os.getcwd(), "text_log.log")

logging.basicConfig(level=logging.INFO,
    format="%(levelname)s - %(asctime)s - %(msg)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(logging_path), # For debug
        logging.StreamHandler(),
    ])

def magic_series(grid):
    """ Check if grid satisfies the definition
        series[k] == sum(series[i] == k) """
    return (grid.sum(1) == np.where(grid.T)[1]).all()

class Domain(object):

    def __init__(self, length):
        self.length = length
        self.grid = np.empty((length, length))
        self.grid[:] = np.nan
        self.numbers = np.linspace(0, length-1, length)

    def __str__(self):
        return str(self.grid)

    def __repr__(self):
        return str(self.to_numbers())

    def __setitem__(self, position, value):
        if isinstance(position, (int, np.integer)):
            self.grid[:, position] = \
                np.array(range(self.length)) == value
        else:
            assert len(position) == 2
            self.grid[position] = value

    def __getitem__(self, index):
        return self.grid[index]

    def __iter__(self):
        # Last missing column
        missing_positions = np.where(np.isnan(self.grid).max(0))[0]
        if missing_positions.size:
            position = missing_positions.max()
            for value in np.where(np.isnan(self.grid[:, position]))[0]:
                yield value, position

    def to_numbers(self):
        """ Convert 2-D domain into 1-D array """
        return np.dot(self.numbers, self.grid)

    def prune(self): # TODO
        """ Prune unfeasible values from domain """
        return prune(self)

    def search(self):
        """ Walk through domain and try each available item """
        results = set()
        temp_domain = copy.deepcopy(self)
        for value, position in self:
            temp_domain[position] = value
            feasibile = temp_domain.prune()
            if not feasibile:
                return set()

            # If no missing values, test and save
            if not np.isnan(temp_domain.to_numbers()).any() and \
                    feasibile and \
                    temp_domain.magic_series():
                results.add(repr(temp_domain))

            # Save all previous results
            results |= temp_domain.search()
        return results

    def magic_series(self):
        """ Check magic """
        return magic_series(self.grid)

    def feasibility_test(self):
        """ Test domain feasibility
            ((b == 1) & (x == v)) | ((b == 0) & (x != v)) """
        values, positions = np.mgrid[:self.length, :self.length]
        feasibility = np.logical_or(np.isnan(self.grid), np.equal(self.grid,
            np.equal(values, np.repeat([self.to_numbers()], self.length,
                axis=0))))
        return feasibility

if __name__ == "__main__":
    for i in range(4, 50):
        t0 = time.time()
        d = Domain(i)
        result = d.search()
        logging.info("{} finished in {} sec: {}"\
            .format(i, round(time.time() - t0, 5), result))
