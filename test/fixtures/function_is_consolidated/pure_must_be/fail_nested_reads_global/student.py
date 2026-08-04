MAKS = 0.2


def arvuta(hind):
    def sisemine():
        return hind * (1 + MAKS)

    return sisemine()


print(arvuta(100))
