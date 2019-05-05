class EntityCounter:
    def __init__(self):
        self.counter = -1

    def next(self):
        self.counter += 1
        return self.counter

    def last(self):
        return self.counter
