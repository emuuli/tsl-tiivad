def inner(x):
    return x + 1


def outer(x):
    return inner(x) * 2
