def tekita():
    return Dog()


class Dog:
    def bark(self):
        return "auh"


print(tekita().bark())
