class Auto:
    def __init__(self, mark):
        self.mark = mark


import sys


def loo_auto(mark):
    return sys.modules[__name__].Auto(mark)
