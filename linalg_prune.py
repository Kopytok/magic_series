def prune_sum_eq_len(domain):
    # domain.to_numbers()
    return False

def prune(domain):
    """ Prune using listed functions """
    constraints = [
        prune_sum_eq_len,
    ]
    changed = feasible = True
    while changed and feasible:
        changed = any([func(domain) for func in constraints])
        feasible = domain.feasibility_test().all()
    return feasible
