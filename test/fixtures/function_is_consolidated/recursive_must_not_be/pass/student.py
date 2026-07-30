def arvuta(n):
    tulemus = 1
    for i in range(1, n + 1):
        tulemus *= i
    return tulemus


print(arvuta(5))
