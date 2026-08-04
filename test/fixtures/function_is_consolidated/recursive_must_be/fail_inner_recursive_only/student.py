def arvuta(n):
    def sisemine(k):
        if k <= 1:
            return 1
        return k * sisemine(k - 1)

    return sisemine(n)


print(arvuta(5))
