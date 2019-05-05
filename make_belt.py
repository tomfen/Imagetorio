import math
import sys

import cv2
import numpy as np

try:
    from dither.dither import dither
except ImportError:
    print('Failed to import dither library. Processing may be slow.', file=sys.stderr)
    from pydither import dither

from blueprint import Blueprint
from direction import Direction
from entitycounter import EntityCounter


available = [
    # comment out items you don't want to use
    # BGR format
    ([ 43.,  70.,  76.], 'firearm-magazine'),
    ([ 43.,  43.,  73.], 'piercing-rounds-magazine'),
    ([ 40., 113.,  31.], 'uranium-rounds-magazine'),
    ([ 54., 173.,  59.], 'battery-equipment'),
    ([183., 135.,  88.], 'slowdown-capsule'),
    ([ 51.,  56.,  73.], 'cluster-grenade'),
    ([115., 116., 117.], 'discharge-defense-equipment'),
    ([130.,  89.,  89.], 'discharge-defense-remote'),
    ([ 44.,  50.,  59.], 'gate'),
    ([ 56., 150.,  83.], 'poison-capsule'),
    ([ 59.,  63.,  62.], 'grenade'),
    ([ 89., 107., 203.], 'belt-immunity-equipment'),
    ([ 62.,  77.,  91.], 'land-mine'),
    ([ 67.,  71.,  75.], 'pistol'),
    ([147., 110., 127.], 'production-science-pack'),
    ([154., 138.,  90.], 'chemical-science-pack'),
    ([117., 112., 110.], 'military-science-pack'),
    ([102., 129., 104.], 'logistic-science-pack'),
    ([ 98.,  90., 136.], 'automation-science-pack'),
    ([154., 151., 151.], 'space-science-pack'),
    ([114., 135., 149.], 'utility-science-pack'),
    ([ 39.,  62., 120.], 'shotgun-shell'),
    ([ 68.,  77.,  89.], 'piercing-shotgun-shell'),
    ([ 72.,  81., 104.], 'combat-shotgun'),
    ([ 61.,  64.,  69.], 'submachine-gun'),
    ([122., 102.,  99.], 'solar-panel-equipment'),
    ([ 77.,  86.,  91.], 'stone-wall'),

    ([103.,  98.,  92.], 'assembling-machine-2'),
    ([ 89., 111., 112.], 'assembling-machine-3'),
    ([ 53.,  83., 159.], 'advanced-circuit'),
    ([ 64.,  71.,  81.], 'burner-inserter'),
    ([ 98.,  81.,  56.], 'cliff-explosives'),
    ([  0.,   0.,   0.], 'coal'),
    ([113., 114., 115.], 'concrete'),
    ([ 46.,  66., 113.], 'copper-ore'),
    ([ 67.,  82., 141.], 'copper-plate'),
    ([ 76.,  94., 133.], 'copper-cable'),
    ([ 78.,  83.,  84.], 'crude-oil-barrel'),
    ([ 54., 138., 109.], 'electronic-circuit'),
    ([ 52., 129.,  70.], 'effectivity-module-3'),
    ([ 50.,  59., 109.], 'explosives'),
    ([107., 102., 104.], 'express-transport-belt'),
    ([100., 103., 120.], 'fast-transport-belt'),
    ([ 82.,  79.,  75.], 'fast-inserter'),
    ([ 81.,  62.,  80.], 'filter-inserter'),
    ([ 56., 127.,  66.], 'green-wire'),
    ([ 68.,  91., 113.], 'heavy-oil-barrel'),
    ([ 56.,  74., 143.], 'heat-pipe'),
    ([ 58.,  83., 112.], 'inserter'),
    ([ 86.,  74.,  56.], 'iron-ore'),
    ([100.,  98.,  99.], 'iron-plate'),
    ([ 87.,  95., 104.], 'iron-chest'),
    ([113., 108., 106.], 'lab'),
    ([ 56., 103., 121.], 'light-oil-barrel'),
    ([100.,  72.,  90.], 'logistic-chest-active-provider'),
    ([ 74., 112.,  74.], 'logistic-chest-buffer'),
    ([ 63.,  73., 120.], 'logistic-chest-passive-provider'),
    ([105.,  98.,  77.], 'logistic-chest-requester'),
    ([ 59.,  95., 110.], 'logistic-chest-storage'),
    ([ 35.,  84.,  85.], 'landfill'),
    ([ 54.,  60., 105.], 'long-handed-inserter'),
    ([ 69., 103.,  82.], 'lubricant-barrel'),
    ([ 76.,  90.,  96.], 'pipe'),
    ([150., 150., 153.], 'plastic-bar'),
    ([102., 106., 107.], 'petroleum-gas-barrel'),
    ([168., 100., 113.], 'processing-unit'),
    ([ 59., 111., 157.], 'productivity-module'),
    ([ 99.,  86.,  73.], 'rail-chain-signal'),
    ([ 40.,  40., 150.], 'red-wire'),
    ([ 92.,  91.,  83.], 'solar-panel'),
    ([ 60.,  60.,  63.], 'solid-fuel'),
    ([153., 130.,  59.], 'speed-module'),
    ([122., 132., 132.], 'steel-plate'),
    ([255., 255., 255.], 'small-lamp'),
    ([ 53.,  91.,  92.], 'stack-inserter'),
    ([117., 110., 115.], 'steel-chest'),
    ([ 59., 128., 109.], 'sulfuric-acid-barrel'),
    ([ 96., 100., 105.], 'stack-filter-inserter'),
    ([ 78.,  87.,  94.], 'storage-tank'),
    ([ 57.,  71.,  80.], 'stone'),
    ([ 98., 102., 102.], 'stone-brick'),
    ([ 74., 139., 153.], 'sulfur'),
    ([ 97., 112., 120.], 'transport-belt'),
    ([ 32., 116.,  74.], 'uranium-ore'),
    ([ 43., 166.,  61.], 'uranium-235'),
    ([ 41.,  76.,  41.], 'uranium-238'),
    ([101., 103.,  96.], 'water-barrel'),
    ([ 51.,  72., 114.], 'wood'),
    ([ 56.,  92., 118.], 'wooden-chest'),
]

palette = [x[0] for x in available]
items = [x[1] for x in available]


def image_resize(image, width=None, height=None, horizontal=False, inter=cv2.INTER_AREA):
    (h, w) = image.shape[:2]

    if width is None:
        r = height / float(h)
        wb, hb = (int(math.ceil(w * r)), height)
    else:
        r = width / float(w)
        wb, hb = (width, int(math.ceil(h * r)))

    if horizontal:
        dim = wb * 4, hb * 2
    else:
        dim = wb * 2, hb * 4

    return cv2.resize(image, dim, interpolation=inter)


def bit_vector_to_int(arr):
    ret = 0

    for i in range(len(arr)):
        ret |= int(arr[i] << i)

    return ret


def print_requirements(ids):

    reqs = []

    for i, a in enumerate(available):
        count = np.sum(ids == i)
        name = a[1]

        reqs.append((name, count))

    reqs = sorted(reqs, key=lambda x: x[1], reverse=True)

    for i, (name, count) in enumerate(reqs):
        if count > 0:
            print((str(i+1)+'. ').ljust(4) + name.ljust(31) + str(count).rjust(6))


def put_canvas(blueprint, counter, x, y, length):
    for i in range(length):
        belt = {'entity_number': counter.next(), 'name': 'express-transport-belt', 'position': {'x': x, 'y': y-i}}
        blueprint['blueprint']['entities'].append(belt)


def put_spliter(blueprint, counter, x, y):
    UNDER = 'express-underground-belt'
    BELT = 'express-transport-belt'
    SPLIT = 'express-splitter'

    if x % 2 == 0:
        entities = [
         {'entity_number': counter.next(), 'name': UNDER, 'position': {'x': x,    'y': y},   'type': 'output'},
         {'entity_number': counter.next(), 'name': BELT,  'position': {'x': x-1,  'y': y+4}, 'direction': Direction.E},
         {'entity_number': counter.next(), 'name': UNDER, 'position': {'x': x,    'y': y+3}, 'type': 'input'},
         {'entity_number': counter.next(), 'name': BELT,  'position': {'x': x,    'y': y+4}},
         {'entity_number': counter.next(), 'name': BELT,  'position': {'x': x,    'y': y+6}},
         {'entity_number': counter.next(), 'name': SPLIT, 'position': {'x': x-.5, 'y': y+5}}]
    else:
        entities = [
         {'entity_number': counter.next(), 'name': BELT,  'position': {'x': x,    'y': y}},
         {'entity_number': counter.next(), 'name': SPLIT, 'position': {'x': x-.5, 'y': y+2}},
         {'entity_number': counter.next(), 'name': BELT,  'position': {'x': x-1,  'y': y+1}, 'direction': Direction.E},
         {'entity_number': counter.next(), 'name': BELT,  'position': {'x': x,    'y': y+1}},
         {'entity_number': counter.next(), 'name': UNDER, 'position': {'x': x,    'y': y+3}, 'type': 'output'},
         {'entity_number': counter.next(), 'name': UNDER, 'position': {'x': x,    'y': y+6}, 'type': 'input'}]

    blueprint['blueprint']['entities'].extend(entities)


def connect(wire, first, second, first_circuit=1, second_circuit=1):
    ent2id = second['entity_number']

    if 'connections' not in first:
        first['connections'] = {}

    if first_circuit not in first['connections']:
        first['connections'][first_circuit] = {}

    if wire not in first['connections'][first_circuit]:
        first['connections'][first_circuit][wire] = []

    first['connections'][first_circuit][wire].append({'entity_id': ent2id, 'circuit_id': second_circuit})


def put_decoder(blueprint, counter, x, y):
    belts = [
        {'entity_number': counter.next(), 'name': 'express-underground-belt', 'position': {'x': x, 'y': y}, 'type': 'output'},
        {'entity_number': counter.next(), 'name': 'express-underground-belt', 'position': {'x': x, 'y': y+9}, 'type': 'input'},
    ]

    requester = {'entity_number': counter.next(),
                 'name': 'logistic-chest-requester',
                 'position': {'x': x, 'y': y+11},
                 'control_behavior': {'circuit_mode_of_operation': 1}
                 }

    multiplier = {'entity_number': counter.next(),
                  'name': 'arithmetic-combinator',
                  'position': {'x': x, 'y': y+5.5},
                  'direction': Direction.S,
                  'control_behavior': {
                   'arithmetic_conditions': {
                    'first_signal': {'type': 'virtual', 'name': 'signal-each'},
                    'second_constant': 5,
                    'operation': '*',
                    'output_signal': {'type': 'virtual', 'name': 'signal-each'}
                   }}}

    inserter = {'entity_number': counter.next(),
                'name': 'stack-filter-inserter',
                'position': {'x': x, 'y': y+10},
                'direction': Direction.S,
                'control_behavior': {
                    'circuit_mode_of_operation': 1,
                    'circuit_read_hand_contents': True
                },
                'override_stack_size': 1}

    pulse_conv = {'entity_number': counter.next(),
                  'name': 'decider-combinator',
                  'position': {'x': x, 'y': y+13.5},
                  'direction': Direction.S,
                  'control_behavior': {
                   'decider_conditions': {
                    'first_signal': {'type': 'virtual', 'name': 'signal-anything'},
                    'constant': 0, 'comparator': '>',
                    'output_signal': {'type': 'virtual', 'name': 'signal-I'},
                    'copy_count_from_input': False
                   }}}

    bit_shifter = {'entity_number': counter.next(),
                   'name': 'arithmetic-combinator',
                   'position': {'x': x, 'y': y+19.5},
                   'control_behavior': {
                    'arithmetic_conditions': {
                     'first_signal': {'type': 'virtual', 'name': 'signal-each'},
                     'second_signal': {'type': 'virtual', 'name': 'signal-I'},
                     'operation': '>>',
                     'output_signal': {'type': 'virtual','name': 'signal-each'}
                    }}}

    bit_and = {'entity_number': counter.next(),
               'name': 'arithmetic-combinator',
               'position': {'x': x, 'y': y+17.5},
               'control_behavior': {
                'arithmetic_conditions': {
                 'first_signal': {'type': 'virtual', 'name': 'signal-each'},
                 'second_constant': 1,
                 'operation': 'AND',
                 'output_signal': {'type': 'virtual', 'name': 'signal-each'}
                }}}

    it_counter = {'entity_number': counter.next(),
                  'name': 'arithmetic-combinator',
                  'position': {'x': x, 'y': y+15.5},
                  'direction': Direction.S,
                  'control_behavior': {
                   'arithmetic_conditions': {
                    'first_signal': {'type': 'virtual', 'name': 'signal-I'},
                    'second_constant': 1,
                    'operation': '*',
                    'output_signal': {'type': 'virtual', 'name': 'signal-I'}
                   }}}

    divider = {'entity_number': counter.next(),
               'name': 'arithmetic-combinator',
               'position': {'x': x, 'y': y+22.5},
               'direction': Direction.S,
               'control_behavior': {
                'arithmetic_conditions': {
                 'first_signal': {'type': 'virtual', 'name': 'signal-I'},
                 'second_constant': 32,
                 'operation': '/',
                 'output_signal': {'type': 'virtual', 'name': 'signal-G'}
                }}}

    connect('green', multiplier,  requester,  first_circuit=2)
    connect('green', inserter,    multiplier, second_circuit=1)
    connect('red',   pulse_conv,  inserter,   first_circuit=1)
    connect('red',   bit_shifter, it_counter, first_circuit=1, second_circuit=2)
    connect('red',   bit_shifter, divider,    first_circuit=1, second_circuit=1)
    connect('green', bit_shifter, bit_and,    first_circuit=2, second_circuit=1)
    connect('green', bit_and,     inserter,   first_circuit=2)
    connect('green', it_counter,  it_counter, first_circuit=1, second_circuit=2)
    connect('red',   it_counter,  pulse_conv, first_circuit=1, second_circuit=2)

    entities = [requester, multiplier, inserter, pulse_conv, bit_shifter, bit_and, it_counter, divider]

    blueprint['blueprint']['entities'].extend(belts)
    blueprint['blueprint']['entities'].extend(entities)

    if x % 7 == 0:
        for _y in [y+7, y+12, y+21]:
            pole = {
                "entity_number": counter.next(),
                "name": "medium-electric-pole",
                "position": {"x": x, "y": _y}
            }

            blueprint["blueprint"]["entities"].append(pole)

    if x % 4 == 0:
        roboport = {
            "entity_number": counter.next(),
            "name": "roboport",
            "position": {"x": x+1.5, "y": y+2.5}
        }

        blueprint["blueprint"]["entities"].append(roboport)

    return divider, bit_shifter


def main():
    if len(sys.argv) < 3:
        print('Usage: python make_belt.py image_path height')
        exit(1)

    image_path, belt_height = sys.argv[1], int(sys.argv[2])

    img = cv2.imread(image_path)
    img = image_resize(img, height=belt_height)

    dithered, ids = dither(img, palette=palette, out='both', method='fs')

    cv2.imshow('image', dithered)
    cv2.waitKey(500)

    print_requirements(ids)

    height, width = ids.shape

    blueprint = Blueprint.empty()

    counter = EntityCounter()

    for x in range(width//2):
        column_left = ids[:, x*2]
        column_right = ids[:, x*2+1]

        put_canvas(blueprint, counter, x, -1, belt_height)
        put_spliter(blueprint, counter, x, 0)
        divider, bit_shifter = \
            put_decoder(blueprint, counter, x, 7)

        entity_y = 31

        for y in range(0, height, 16):
            strip_left = column_left[y:y+16]
            strip_right = column_right[y:y+16]

            strip_number = y//16

            encoded = [val for pair in zip(strip_right, strip_left) for val in pair]

            filters = []

            for item_idx, item in enumerate(items):
                item_bit_vector = [x == item_idx for x in encoded]

                integer = bit_vector_to_int(item_bit_vector)

                if integer == 0:
                    continue

                filters.append({
                    "count": integer,
                    "index": len(filters) % 18 + 1,
                    "signal": {"type": "item", "name": item},
                })

            decider_combinator = {
                "connections": {
                    "1": {"red": [{
                        "entity_id": divider["entity_number"],
                        "circuit_id": 2}]},
                    "2": {"green": [{
                        "entity_id": bit_shifter["entity_number"],
                        "circuit_id": 1}]}

                } if strip_number == 0 else {
                    "1": {"red": [{
                        "entity_id": decider_combinator["entity_number"],
                        "circuit_id": 1}]},
                    "2": {"green": [{
                        "entity_id": decider_combinator["entity_number"],
                        "circuit_id": 2}]}
                },
                "control_behavior": {
                    "decider_conditions": {
                        "first_signal": {"type": "virtual", "name": "signal-G"},
                        "constant": strip_number,
                        "comparator": "=",
                        "output_signal": {"type": "virtual", "name": "signal-everything"},
                        "copy_count_from_input": "true"
                    }
                },
                "direction": Direction.N,
                "entity_number": counter.next(),
                "name": "decider-combinator",
                "position": {"x": x, "y": entity_y + 0.5}
            }

            constant_combinator1 = {
                "connections": {
                    "1": {
                        "green": [{
                            "entity_id": counter.last(),
                            "circuit_id": 1}]}},
                "control_behavior": {"filters": filters[:18]},
                "entity_number": counter.next(),
                "name": "constant-combinator",
                "position": {"x": x, "y": entity_y + 2}
            }

            blueprint["blueprint"]["entities"].append(decider_combinator)
            blueprint["blueprint"]["entities"].append(constant_combinator1)

            if len(filters) > 18:
                constant_combinator2 = {
                    "connections": {
                        "1": {
                            "green": [{
                                "entity_id": counter.last(),
                                "circuit_id": 1,
                            }]
                        }
                    },
                    "control_behavior": {"filters": filters[18:]},
                    "entity_number": counter.next(),
                    "name": "constant-combinator",
                    "position": {"x": x, "y": entity_y + 3}
                }

                blueprint["blueprint"]["entities"].append(constant_combinator2)

            if x % 7 == 0:
                pole = {"entity_number": counter.next(),
                        "name": "medium-electric-pole",
                        "position": {"x": x, "y": entity_y + 3}}

                blueprint["blueprint"]["entities"].append(pole)

            entity_y += 4

    print()
    print(Blueprint.export_blueprint(blueprint))


if __name__ == '__main__':
    main()
