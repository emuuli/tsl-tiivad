class Dog:
    def bark(self):
        return "auh"


class Owner:
    def __init__(self, dog):
        self.dog = dog

    def walk(self):
        return self.dog
