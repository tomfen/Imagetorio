import math
from itertools import product, chain

import numpy as np

CABLE_REACH = 10.03


class Group:
    def __init__(self):
        self.lamps = []
        self.connections = []


def distance(l1, l2):
    x1, y1 = l1
    x2, y2 = l2

    return math.sqrt((x1-x2)**2 + (y1-y2)**2)


closest = product([x for x in range(math.floor(-CABLE_REACH), math.ceil(CABLE_REACH+1))], repeat=2)
closest = [x for x in closest if 0 < distance((0, 0), x) < CABLE_REACH]
closest = sorted(closest, key=lambda x: distance((0, 0), x))


def try_connect(g1, g2):
    for lamp1 in g1.lamps:
        for lamp2 in g2.lamps:

            if distance(lamp1, lamp2) < CABLE_REACH:
                return lamp1, lamp2
    return None


def assert_groups_contain(groups, lamps):
    grouped = []

    for g in groups:
        for lamp in g.lamps:
            grouped.append(lamp)

    for l in grouped:
        if l not in lamps:
            raise Exception('lamp %s not present' % str(l))

    for l in lamps:
        if l not in grouped:
            raise Exception('lamp %s not present' % str(l))


def connect_all(lamps):

    groups = []

    # group = Group()

    # for lamp1 in lamps:
    #     if not group.lamps:
    #         group.lamps.append(lamp1)
    #
    #     else:
    #         conn = False
    #
    #         for lamp2 in reversed(group.lamps):
    #
    #             d = distance(lamp1, lamp2)
    #
    #             if d <= CABLE_REACH:
    #                 group.lamps.append(lamp1)
    #                 group.connections.append((lamp1, lamp2))
    #                 conn = True
    #                 break
    #
    #         if not conn:
    #             groups.append(group)
    #             group = Group()

    for l in lamps:
        group = Group()
        group.lamps = [l]
        groups.append(group)

    assert_groups_contain(groups, lamps)

    disjoint = []

    while groups:
        g = groups.pop(-1)

        found = False
        for g2 in reversed(groups):
            conn = try_connect(g, g2)
            if conn:
                found = True
                g2.lamps.extend(g.lamps)
                g2.connections.extend(g.connections)
                g2.connections.append(conn)
                break

        if not found:
            print('Group of: %i ' % len(g.lamps))
            disjoint.append(g)

    assert_groups_contain(disjoint, lamps)

    return disjoint


def solve(img):

    lamps_by_color = {x: [] for x in range(8)}

    stride = 7

    for b in range(0, img.shape[0], stride):

        band = img[b:b+stride, :]

        height, width = band.shape

        for x in range(width):
            for _y in range(height):
                y = _y + b

                if 7 <= x % 18 <= 8 and 7 <= y % 18 <= 8:
                    continue

                color = img[y][x]

                lamps_by_color[color].append((x, y))

    return chain.from_iterable(connect_all(lamps_by_color[color]) for color in range(8))
