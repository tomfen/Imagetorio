from direction import Direction


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, direction, distance):
        if direction == Direction.N:
            self.y += distance
        if direction == Direction.E:
            self.x += distance
        if direction == Direction.S:
            self.y -= distance
        if direction == Direction.W:
            self.x -= distance