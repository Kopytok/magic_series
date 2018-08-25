def prune_sum_eq_len(domain):
    return False

def prune(domain):
    """ Prune using listed functions """
    constraints = [
        prune_sum_eq_len,
    ]
    changed = True
    while changed:
        changed = any([func(domain) for func in constraints])
    return domain.feasibility_test().all()
