LOENDUR = 0


def arvuta(a):
    global LOENDUR
    LOENDUR = LOENDUR + a
    return LOENDUR


print(arvuta(5))
