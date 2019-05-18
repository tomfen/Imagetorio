import math
import re
import sys

import click
import cv2
import numpy as np
import pyperclip
from blueprint import Blueprint
from direction import Direction
from entitycounter import EntityCounter
from item_colors import colors

try:
    from dither.dither import dither
except ImportError:
    print('Failed to import dither library. Processing may be slow.', file=sys.stderr)
    from pydither import dither


def image_resize(image, width=None, height=None, horizontal=False, inter=cv2.INTER_AREA):
    (h, w) = image.shape[:2]

    ratio_horizontal = width / w if width else 1
    ratio_vertical = height / h if height else 1

    r = min(ratio_horizontal, ratio_vertical)

    wb, hb = (int(math.ceil(w * r)),
              int(math.ceil(h * r)))

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

    required = []

    for i, a in enumerate(colors):
        count = np.sum(ids == i)
        name = a

        required.append((name, count))

    required = sorted(required, key=lambda x: x[1], reverse=True)

    for i, (name, count) in enumerate(required):
        if count > 0:
            print((str(i+1)+'. ').ljust(4) + name.ljust(31) + str(count).rjust(6))


def put_canvas(blueprint, counter, x, y, length):
    for i in range(length):
        belt = {'entity_number': counter.next(), 'name': 'express-transport-belt', 'position': {'x': x, 'y': y-i}}
        blueprint['blueprint']['entities'].append(belt)


def put_splitter(blueprint, counter, x, y):
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


def load_palette(path):
    palette = []
    names = []

    with open(path, 'r') as file:
        for item_name in file.readlines():
            item_name = item_name.strip()

            if not re.match(r'^[a-z]', item_name):
                continue

            if item_name in colors:
                names.append(item_name)
                palette.append(colors[item_name])
            else:
                print('Unknown item name: %s' % item_name, file=sys.stderr)

    return palette, names


def put_memory(blueprint, counter, x, item_number, divider, bit_shifter, id_list, names):
    entity_y = item_number

    for item_number in range(0, len(id_list), 32):

        strip = id_list[item_number:(item_number + 32)]
        strip_number = item_number // 32

        filters = []

        for item_idx, item in enumerate(names):
            item_bit_vector = [x == item_idx for x in strip]

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


def get_slices(id_matrix, direction):
    h, w = id_matrix.shape

    if direction == 's':
        return [id_matrix[:, x] for x in range(w)]
    elif direction == 'w':
        return [reversed(id_matrix[y, :]) for y in range(h)]
    elif direction == 'n':
        return [reversed(id_matrix[:, x]) for x in reversed(range(w))]
    elif direction == 'e':
        return [id_matrix[y, :] for y in reversed(range(h))]


@click.command()
@click.argument('image_path')
@click.option('-w', 'width',     default=None, type=click.INT, help='Maximum width in belts.')
@click.option('-h', 'height',    default=None, type=click.INT, help='Maximum height in belts.')
@click.option('-d', 'direction', default='w',  type=click.Choice(['n', 'w', 's', 'e']),
              help='Direction of the printing part from the canvas.')
@click.option('-i', 'itemfile',     default='items.txt', help='File with a list of items to use. If not specified it '
                                                           'will load "items.txt"')
@click.option('-o', 'output',    default=None, help='Output file. If not specified the blueprint will be copied'
                                                    'into clipboard.')
def main(image_path, width, height, direction, itemfile, output):

    horizontal = direction == 'e' or direction == 'w'

    img = cv2.imread(image_path)
    img = image_resize(img, width=width, height=height, horizontal=horizontal)

    palette, items = load_palette(itemfile)

    dithered, id_matrix = dither(img, palette=palette, out='both', method='fs', gamma_correction=2.2)

    cv2.imshow('image', dithered)
    cv2.waitKey(500)

    print_requirements(id_matrix)

    blueprint = Blueprint.empty(name=image_path)

    counter = EntityCounter()

    slices = get_slices(id_matrix, direction)

    for c in range(len(slices)//2):

        slice_first = slices[c*2+1]
        slice_second = slices[c*2]
        id_list = [val for pair in zip(slice_first, slice_second) for val in pair]

        put_canvas(blueprint, counter, c, -1, len(id_list) // 8)
        put_splitter(blueprint, counter, c, 0)
        divider, bit_shifter = \
            put_decoder(blueprint, counter, c, 7)
        put_memory(blueprint, counter, c, 31, divider, bit_shifter, id_list, items)

    string = Blueprint.export_blueprint(blueprint)

    if output:
        with open(output, 'w') as file:
            file.write(string)
    else:
        pyperclip.copy(string)
        print('Copied blueprint to clipboard')

    click.pause(info='Press any key to continue ...', err=False)


if __name__ == '__main__':
    main()
