import argparse
import math
from PIL import Image
import numpy as np
import pyperclip
from blueprint import Blueprint
from items import all_signals
from PIL import ImageEnhance
from tqdm import tqdm

IN_RED = 1
IN_GREEN = 2
OUT_RED = 3
OUT_GREEN = 4
ELECTRICITY = 5

SUBSTATION = 28


def pairwise(lst):
    return zip(lst, lst[1:])


def get_signal(i):
    return all_signals[i]


items_no = 1000


def make_stripe(x_start, y_start, idx_start, height, signal):
    entities = []
    wires = []

    idx = idx_start
    for y in range(height):
        if (x_start + 2) % SUBSTATION in (0, 1) and (y + 2) % SUBSTATION in (0, 1):
            continue

        entities.append(
            {
                "entity_number": idx,
                "name": "small-lamp",
                "position": {"x": 0.5 + x_start, "y": 0.5 + y_start + y},
                "control_behavior": {
                    "use_colors": "true",
                    "rgb_signal": get_signal(signal + y),
                    "color_mode": 2,
                },
                "always_on": "true",
            },
        )

        idx += 1

    wires = [
        [entity["entity_number"], IN_GREEN, entity["entity_number"] + 1, IN_GREEN]
        for entity in entities[:-1]
    ]

    return entities, wires, idx


def make_substations(x0, y0, x1, y1, idx):
    entities = []
    wires = []

    for y in range(y0, y1, SUBSTATION):
        row = []
        for x in range(x0, x1, SUBSTATION):
            row.append(
                {
                    "entity_number": idx,
                    "name": "substation",
                    "quality": "legendary",
                    "position": {"x": x, "y": y},
                }
            )
            idx += 1

        wires += [
            [s0["entity_number"], ELECTRICITY, s1["entity_number"], ELECTRICITY]
            for s0, s1 in pairwise(row)
        ]

        entities += row

    return entities, wires, idx


def make_lamp(x, y, width, height, idx_start):
    entities = []
    wires = []
    idx = idx_start
    signal = 0

    for x_ in range(width):
        last_idx = idx
        entities_stripe, wires_stripe, idx = make_stripe(x + x_, y, idx, height, signal)

        entities += entities_stripe
        wires += wires_stripe

        signal += height
        if signal + height > items_no:
            signal = 0
        else:
            wires.append([last_idx, IN_GREEN, idx, IN_GREEN])

    return entities, wires, idx


def make_animation(data):
    data = data.astype("int32")
    packed = data[:, :, :, 0] * 256 * 256 + data[:, :, :, 1] * 256 + data[:, :, :, 2]

    frames, height, width = packed.shape

    chunk_no = math.ceil(width / (items_no // height))

    chunks = np.array_split(packed, chunk_no, axis=2)

    chunks_flattened = []

    for chunk in chunks:
        f, h, w = chunk.shape
        flattened = np.reshape(chunk, newshape=(f, h * w), order="F")
        chunks_flattened.append((w, flattened))

    entities = []
    wires = []
    idx = 1

    entities, wires, idx = make_substations(-1, -1, width + 1, height + 1, idx)

    x = 0
    for w, chunk in tqdm(chunks_flattened):
        chunk_entities, chunk_wires, idx = make_encoder(x, -4, w, chunk, idx)
        entities += chunk_entities
        wires += chunk_wires

        # lamp_entities, lamp_wires, idx = make_lamp(x, 0, w, height, idx)
        # entities += lamp_entities
        # wires += lamp_wires

        x += w

    return entities, wires


def make_encoder(x, y, width, chunk, idx):
    entities = []
    wires = []

    for frame_no, frame in enumerate(chunk):
        y_, x_ = divmod(frame_no, width)

        y_ += y_ // 5

        constant_combinator = {
            "entity_number": idx,
            "name": "constant-combinator",
            "position": {"x": 0.5 + x + x_, "y": 0.5 + y - y_ * 3 - 2},
            "control_behavior": {
                "sections": {
                    "sections": [
                        {
                            "index": 1,
                            "filters": [
                                {
                                    "index": signal + 1,
                                    "type": "item",
                                    "comparator": "=",
                                    "count": int(pixel),
                                }
                                | get_signal(signal)
                                for signal, pixel in enumerate(frame)
                            ],
                        }
                    ]
                }
            },
        }
        decider_combinator = {
            "entity_number": idx + 1,
            "name": "decider-combinator",
            "position": {"x": 0.5 + x + x_, "y": y - y_ * 3},
            "direction": 8,
            "control_behavior": {
                "decider_conditions": {
                    "conditions": [
                        {
                            "first_signal": {"type": "virtual", "name": "signal-dot"},
                            "comparator": "=",
                            "constant": frame_no,
                            "first_signal_networks": {"red": "false", "green": "true"},
                        }
                    ],
                    "outputs": [
                        {
                            "signal": {"type": "virtual", "name": "signal-everything"},
                            "networks": {"red": "true", "green": "false"},
                        }
                    ],
                }
            },
        }
        entities.append(constant_combinator)
        entities.append(decider_combinator)

        wires.append([idx, 1, idx + 1, 1])

        idx += 2

    deciders = entities[1::2]

    wires += [
        [d1["entity_number"], IN_GREEN, d2["entity_number"], IN_GREEN]
        for d1, d2 in pairwise(deciders)
    ]
    wires += [
        [d1["entity_number"], OUT_GREEN, d2["entity_number"], OUT_GREEN]
        for d1, d2 in pairwise(deciders)
    ]

    return entities, wires, idx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()

    frames = []

    with Image.open(args.path) as gif:
        gif.seek(0)

        try:
            while 1:
                frame = gif.convert("RGBA")
                frames.append(frame)
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass

    # frames = [f.resize((187, 105)) for f in frames]

    frames = [ImageEnhance.Contrast(f).enhance(1.5) for f in frames]

    data = np.stack(frames, axis=0)
    entities, wires = make_animation(data)

    bp = {
        "blueprint": {
            "icons": [{"signal": {"name": "small-lamp"}, "index": 1}],
            "entities": entities,
            "wires": wires,
            "item": "blueprint",
            "label": "Lamp",
            "version": 562949954142211,
        }
    }

    string = Blueprint.export_blueprint(bp)
    pyperclip.copy(string)


if __name__ == "__main__":
    main()
