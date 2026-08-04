class Loom:
    def haali(self):
        return "..."


if __name__ == "__main__":
    class Koer(Loom):
        def haali(self):
            return "auh"

    print(Koer().haali())
