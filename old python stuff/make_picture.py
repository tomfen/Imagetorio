import json

import cv2
import numpy as np
from dither import dither

import connector
from blueprint import Blueprint
from entitycounter import EntityCounter

color_signals = [
    'signal-red',
    'signal-green',
    'signal-blue',
    'signal-yellow',
    'signal-pink',
    'signal-cyan',
    'signal-white',
    'signal-black'  # lamp off
]


def palette_to_signal(n):
    return {
        "type": "virtual",
        "name": color_signals[n],
    }


def main():
    img = cv2.imread('..\\pics\\flag.png')
    img = cv2.imread('..\\science.jpg')

    newX, newY = img.shape[1] * .18, img.shape[0] * .18
    img = cv2.resize(img, (int(newX), int(newY)))

    dithered, ids = dither.dither(img, palette='factorio-black', out='both', method='fs')


    # for i in range(8):
    #     cv2.imwrite('%i.png' % i, np.where(ids != i, 0, 255))

    cv2.imwrite('ds.png', dithered)

    height, width = ids.shape

    disjoint = connector.solve(ids)

    blueprint = Blueprint.empty()

    lamps = [[None for _ in range(width)] for _ in range(height)]

    entity_counter = EntityCounter()

    for y in range(height):
        for x in range(width):
            if 7 <= x % 18 <= 8 and 7 <= y % 18 <= 8:
                continue

            color = ids[y][x]
            if color==7: continue

            signal = palette_to_signal(color)

            lamp = {
                "connections": {},
                "control_behavior": {
                        "circuit_condition": {
                            "first_signal": signal,
                            "constant": 0,
                            "comparator": ">"
                        },
                        "use_colors": "true"
                    },
                "entity_number": entity_counter.next(),
                "name": "small-lamp",
                "position": {"x": x, "y": y}
            }

            lamps[y][x] = lamp
            blueprint['blueprint']['entities'].append(lamp)

    for y in range(7, height, 18):
        for x in range(7, width, 18):
            substation = {
                "entity_number": entity_counter.next(),
                "name": "substation",
                "position": {"x": x + .5, "y": y + .5}
            }

            blueprint['blueprint']['entities'].append(substation)

    for g in disjoint:

        for l1, l2 in g.connections:
            x1, y1 = l1
            x2, y2 = l2

            lamp = lamps[y1][x1]

            if not lamp: continue

            entid = lamp["entity_number"]

            key = len(lamps[y2][x2]['connections'])+1

            lamps[y2][x2]['connections'][key] = {
                    "green": [{
                        "entity_id": entid,
                        "circuit_id": 1
                        }]
                    }

    print(Blueprint.export_blueprint(blueprint))


if __name__ == '__main__':
    main()
