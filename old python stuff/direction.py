class Direction:
    N = 0
    NE = 1
    E = 2
    SE = 3
    S = 4
    SW = 5
    W = 6
    NW = 7

    @staticmethod
    def opposite(direction):
        return (direction+4) % 8

    @staticmethod
    def fromstring(s):
        s = s.upper()
        return Direction.__dict__[s]
