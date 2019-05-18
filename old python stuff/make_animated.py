import math

import numpy as np
from blueprint import Blueprint
from entitycounter import EntityCounter
from direction import Direction
import cv2

from point import Point
from pydither import dither


def load_image(img_path):
    img = cv2.imread(img_path)
    dithered, ids = dither(img, method='ordered', palette=[[0, 0, 0], [255, 255, 255]], out='ids')
    cv2.imshow('s', dithered.astype('uint8'))
    cv2.waitKey(0)
    return ids.astype(np.uint32)


def signal_number(n):
    if n < 10:
        name = 'signal-' + str(n)
    elif n < 36:
        name = 'signal-' + chr(ord('A') + n - 10)
    else:
        name = None

    return {
        "type": "virtual",
        "name": name
    }


#
# Process images
#


def fold(arrays):
    ret = np.zeros_like(arrays[0])
    shift = 31

    for array in arrays:
        ret |= array << shift
        shift -= 1

    return ret


def load_frames(path, frame_width):
    img = load_image(path)
    img = img.astype('int32', casting='unsafe')
    width = img.shape[1]
    assert width % frame_width == 0

    return np.stack([img[:, i:i + frame_width] for i in range(0, width, frame_width)])


def make_row(blueprint, start, frames, counter, direction):
    lamps_needed = len(frames[0])
    constant_needed = math.ceil(lamps_needed / 18)

    frames_number = len(frames)
    frame_group_number = math.ceil(frames_number / 32)

    for l in range(lamps_needed):
        # leave sppace for substations
        if 8 <= start.x % 18 <= 9 and 8 <= start.y % 18 <= 9:
            start.move(direction, 1)
            continue

        lamp = {
            "connections": {} if l == 0 else {
                "1": {
                    "green": [{
                        "entity_id": counter.last(),
                        "circuit_id": 1
                    }]
                }
            },
            "control_behavior": {
                "circuit_condition": {
                    "first_signal": signal_number(l),
                    "constant": 0,
                    "comparator": "<"
                },
                "use_colors": "false"
            },
            "entity_number": counter.next(),
            "name": "small-lamp",
            "position": {"x": start.x, "y": start.y}
        }

        start.move(direction, 1)

        blueprint["blueprint"]["entities"].append(lamp)

    start.move(direction, 0.5)
    shift_combinator = {
        "connections": {
            "2": {
                "green": [{
                    "entity_id": counter.last(),
                    "circuit_id": 1
                }]
            }
        },
        "control_behavior": {
            "arithmetic_conditions": {
                "first_signal": {
                    "type": "virtual",
                    "name": "signal-each"
                },
                "second_signal": {
                    "type": "virtual",
                    "name": "signal-dot"
                },
                "operation": "<<",
                "output_signal": {
                    "type": "virtual",
                    "name": "signal-each"
                }
            }
        },
        "direction": direction,
        "entity_number": counter.next(),
        "name": "arithmetic-combinator",
        "position": {"x": start.x, "y": start.y}
    }

    start.move(direction, 1.5)

    blueprint["blueprint"]["entities"].append(shift_combinator)

    first_decider = None
    last_decider = None

    for fg in range(frame_group_number):
        start.move(direction, 0.5)
        decider_combinator = {
            "connections": {
                "2": {
                    "green": [{
                        "entity_id": shift_combinator["entity_number"],
                        "circuit_id": 1,
                    }]
                }
            } if fg == 0 else {
                "1": {
                    "red": [{
                        "entity_id": last_decider["entity_number"],
                        "circuit_id": 1,
                    }]
                },
                "2": {
                    "green": [{
                        "entity_id": last_decider["entity_number"],
                        "circuit_id": 2,
                    }]
                }
            },

            "control_behavior": {
                "decider_conditions": {
                    "first_signal": {
                        "type": "virtual",
                        "name": "signal-info"
                    },
                    "constant": fg,
                    "comparator": "=",
                    "output_signal": {
                        "type": "virtual",
                        "name": "signal-everything"
                    },
                    "copy_count_from_input": "true"
                }
            },
            "direction": direction,
            "entity_number": counter.next(),
            "name": "decider-combinator",
            "position": {"x": start.x, "y": start.y}
        }

        start.move(direction, 2.5)

        last_decider = decider_combinator
        if fg == 0:
            first_decider = decider_combinator
        blueprint["blueprint"]["entities"].append(decider_combinator)

        filters = []

        fg_fold = fold(frames[fg * 32:fg * 32 + 32])

        for s in range(lamps_needed):
            filters.append({
                "count": int(fg_fold[s]),
                "index": (s % 18 + 1),
                "signal": signal_number(s),
            })

        for cc in range(constant_needed):
            constant_combinator = {
                "connections": {
                    "1": {
                        "green": [{
                            "entity_id": counter.last(),
                            "circuit_id": 1
                        }]
                    }
                },
                "control_behavior": {"filters": filters[cc * 18:(cc + 1) * 18]},
                "direction": direction,
                "entity_number": counter.next(),
                "name": "constant-combinator",
                "position": {"x": start.x, "y": start.y}
            }
            start.move(direction, 1)

            blueprint["blueprint"]["entities"].append(constant_combinator)

    return shift_combinator, first_decider


def main():
    # SETTINGS
    img_path = r'C:\Users\Tomek\Desktop\pics\f.bmp'
    frame_width = 36

    frames = load_frames(img_path, frame_width)

    blueprint = Blueprint.empty()

    height, width = frames[0].shape

    ec = EntityCounter()

    last_shift_comb, last_decider = None, None

    for line in range(height):
        start = Point(line, 0)

        row_frames = [F[line, :] for F in frames]

        start.move(Direction.W, 1)

        shift_comb, decider = make_row(blueprint, start, row_frames, ec, Direction.N)

        if last_shift_comb:
            shift_comb["connections"]["1"] = {
                "red": [{
                    "entity_id": last_shift_comb["entity_number"],
                    "circuit_id": 1
                }]
            }

        if last_decider:
            decider["connections"]["1"] = {
                "red": [{
                    "entity_id": last_decider["entity_number"],
                    "circuit_id": 1
                }]
            }

        last_shift_comb, last_decider = shift_comb, decider

    print(Blueprint.export_blueprint(blueprint))


if __name__ == '__main__':
    main()
