class Loendur:
    def arvuta(self, n):
        if n == 0:
            return 0
        return n + self.arvuta(n - 1)


print(Loendur().arvuta(4))
