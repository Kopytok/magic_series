import logging
from functools import reduce

def nan_cnt(lst):
    """ Count missing items in `lst` """
    return len([x for x in lst if x == -1])

def row_sum(lst):
    """ Sum of non-missing items in `lst` """
    return sum(int(x) for x in lst if x > -1)

def prune_sum_eq_len(domain):
    """ Check if sum of digits may be equal to len of series """
    prune_flg = False
    out = domain.copy()
    for value, row in enumerate(out.grid):
        logging.debug("Value: {}\tRow: {}".format(value, row))
        for position, it in enumerate(row):
            logging.debug("Position: {}\tIt: {}".format(position, int(it)))
            if it == -1:
                min_eval = out.eval(value, position, how="min")
                max_eval = out.eval(value, position, how="max")

                constraints = [
                    sum(min_eval) > domain.length,
                    sum(max_eval) < domain.length,
                    sum([t * n for t, n in enumerate(min_eval)]) > domain.length,
                    sum([t * n for t, n in enumerate(max_eval)]) < domain.length,
                ]

                if reduce(lambda x, y: x | y, constraints):
                    prune_flg = True
                    domain.grid[value, position] = 0
        logging.debug("Domain after row check:\n%s" % repr(domain))
    return prune_flg

def prune_last_missing_number(domain):
    """ Fill in the last missing number """
    prune_flg = False
    numbers = domain.to_digits()
    if nan_cnt(numbers) == 1:
        last_value = len(domain) - row_sum(numbers)
        if last_value < len(numbers):
            prune_flg = True
            domain[numbers.index(-1)] = last_value
    return prune_flg

def prune_less_than_possible(domain):
    """ Fill with 0 values less than current number of occurences """
    prune_flg = False
    numbers = domain.to_digits()
    for num in numbers:
        if num > -1:
            num_bag = [x for x in numbers if x == num]
            for value, position in enumerate(num_bag):
                if domain.grid[value, position] == -1:
                    prune_flg = True
                    domain.grid[value, position] = 0
    return prune_flg

def prune_known_row_sum(domain):
    """ Fill row if corresponding value is already solved """
    prune_flg = False
    for position, value in enumerate(domain.to_digits()):
        if domain.nan_cnt(position) and \
                value > -1 and \
                domain.row_sum(position) == value:
            prune_flg = True
            domain.grid[position, :] = \
                [x if x > -1 else 0 for x in domain.grid[position, :]]
    return prune_flg

def prune_fill_column(domain):
    """ Fill column if only 1 item is missing """
    prune_flg = False
    temp = domain.copy()
    for position, col in enumerate(temp.grid.T):
        if nan_cnt(col) == 1:
            prune_flg = True
            col = [x if x > -1 else 1 - row_sum(col) for x in col]
        domain.grid[:, position] = col.copy()
    return prune_flg

def prune_sum_ready(domain):
    """ Decide number at position if already filled corresponding row """
    prune_flg = False
    for value, row in enumerate(domain.grid):
        if -1 not in row and -1 in domain[value]:
            prune_flg = True
            domain[value] = int(sum(row))
    return prune_flg

def prune(domain):
    while domain.feasibility_test():
        constraints = [
            "prune_sum_eq_len",
            "prune_last_missing_number",
            "prune_less_than_possible",
            "prune_fill_column",
            "prune_known_row_sum",
            "prune_sum_ready",
        ]
        changed_flg = False # Track changes
        for func in constraints:
            try:
                prune_flg = eval("%s(domain)" % func)
                changed_flg = changed_flg or prune_flg
                logging.debug("Changed after {} {}:\n{}".format(
                    func, prune_flg, repr(domain)))
            except IndexError as e:
                break
        if not changed_flg:
            break
    return domain

if __name__ == "__main__":
    pass
