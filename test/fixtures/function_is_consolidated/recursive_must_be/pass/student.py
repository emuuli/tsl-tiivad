def arvuta(n):
    if n <= 1:
        return 1
    return n * arvuta(n - 1)


print(arvuta(5))
