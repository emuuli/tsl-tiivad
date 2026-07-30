def util(x):
    return x + 1


class Other:
    def run(self, x):
        return util(x)


class Owner:
    def run(self, x):
        return x * 2
