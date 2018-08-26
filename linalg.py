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
        self.numbers = np.linspace(0, length-1, length)
        self.grid = np.empty((length, length))
        self.grid[:] = np.nan
        self.grid[0,0] = False

    def __str__(self):
        return str(self.grid)

    def __repr__(self):
        return str(self.to_numbers())

    def __setitem__(self, position, value):
        if isinstance(position, (int, np.integer)):
            self.grid[:, position] = \
                np.array(range(self.length)) == value
        else:
            self.grid[position] = value

    def __getitem__(self, index):
        return self.grid[index]

    def __iter__(self):
        """ Generate available values from most right column
            with available values """
        logging.debug("Grid:\n{}".format(self))
        missing_values = self.missing_values()
        logging.debug("Iter missing values:\n{}".format(str(missing_values)))
        missing_mask   = (~np.isnan(missing_values))
        if missing_mask.any():
            position = np.where(missing_mask.max(0))[0][-1]
            available = missing_values[:, position]
            logging.debug("Iter available: {}".format(available))
            for value in available[~np.isnan(available)]:
                yield value, position

    def to_numbers(self):
        """ Convert 2-D domain into 1-D array """
        numbers = np.dot(self.numbers, self.grid)
        return numbers

    def missing_values(self):
        """ Make matrix with only available missing values """
        mask = np.isnan(self.grid)
        values = mask * self.numbers.reshape((-1, 1))
        return np.where(mask, values, np.nan)

    def estimate(self, f="min", how="sum"):
        """ Estimate min or max (position), if `sum`,
            (index * position), if `mult`
            for each missing position """
        mask = np.isnan(self.grid)

        if how == "mult":
            values = np.multiply(*np.mgrid[:self.length, :self.length])
            missing_values = np.where(mask, values, np.nan)
            num = np.multiply(self.to_numbers(), self.numbers)
        else:
            missing_values = self.missing_values()
            num = self.to_numbers()

        clean_bound = np.nan_to_num(missing_values) - \
            np.nan_to_num(num) + np.nansum(num)
        clean_bound = np.where(mask, clean_bound, np.nan)
        est = eval("np.nan%s" % f)(missing_values, 0)
        all_sum = np.nansum(est)
        return clean_bound + all_sum - est

    def prune(self):
        """ Prune unfeasible values from domain """
        return prune(self)

    def search(self):
        """ Walk through domain and try each available item """
        results = set()
        for value, position in self:
            temp_domain = copy.deepcopy(self)
            logging.debug("value: {}, position: {}".format(value, position))
            temp_domain[position] = value
            feasibile = temp_domain.prune()
            if not feasibile:
                continue

            # If no missing values, test and save
            no_missing = not np.isnan(temp_domain.to_numbers()).any()
            if no_missing:
                logging.debug("Full series: {}".format(repr(temp_domain)))
                logging.debug("Magic: {}".format(temp_domain.magic_series()))
            if no_missing and feasibile and temp_domain.magic_series():
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
        feasibility = \
            np.logical_or(
                np.isnan(self.grid),
                np.equal(
                    self.grid,
                    np.equal(
                        values,
                        np.repeat([self.to_numbers()], self.length, axis=0))))
        return feasibility


def main():
    try:
        for i in range(4, 50):
            t0 = time.time()
            d = Domain(i)
            result = d.search()
            logging.info("{} finished in {} sec: {}"\
                .format(i, round(time.time() - t0, 5), result))
    except KeyboardInterrupt as e:
        pass

if __name__ == "__main__":
    main()
