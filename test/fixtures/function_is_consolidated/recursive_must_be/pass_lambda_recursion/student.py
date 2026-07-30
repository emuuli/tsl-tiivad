def arvuta(n):
    samm = lambda k: arvuta(k - 1)
    if n <= 0:
        return 0
    return samm(n)


print(arvuta(3))
