import math
import numpy as np


def distance(c1, c2):
    return np.linalg.norm(c1-c2, 2)


def get_closest(color, palette):
    closest_idx, closest_color = min((x for x in enumerate(palette)), key=lambda x: distance(x[1], color))

    return closest_idx, closest_color


def floyd_steinberg(image, palette):
    img_float = image.astype('float')
    palette = np.asarray(palette, 'float')

    height, width = image.shape[:2]

    dithered = np.zeros((height, width, 3), 'uint8')
    indexes = np.zeros((height, width), 'int')

    for y in range(height):
        for x in range(width):
            color = img_float[y, x]

            closest_idx, closest_color = get_closest(color, palette)

            dithered[y, x] = closest_color
            indexes[y, x] = closest_idx

            error = color - closest_color

            if x < width - 1:
                img_float[y][x + 1] += error * 7 / 16

            if y < height - 1:
                if 0 < x:
                    img_float[y + 1][x - 1] += error * 3 / 16

                img_float[y + 1][x] += error * 5 / 16

                if x < width - 1:
                    img_float[y + 1][x + 1] += error * 1 / 16

    return dithered, indexes


def ordered(image, palette):
    mask = np.asarray([[ 1, 49, 13, 61,  4, 52, 16, 64],
                       [33, 17, 45, 29, 36, 20, 48, 32],
                       [ 9, 57,  5, 53, 12, 60,  8, 56],
                       [41, 25, 37, 21, 44, 28, 40, 24],
                       [ 3, 51, 15, 63,  2, 50, 14, 62],
                       [35, 19, 47, 31, 34, 18, 46, 30],
                       [11, 59,  7, 55, 10, 58,  6, 54],
                       [43, 27, 39, 23, 42, 26, 38, 22]]) / 65.0

    # mask = np.asarray([[ 1,  9,  3, 11],
    #                    [13,  5, 15,  7],
    #                    [ 4, 12,  2, 10],
    #                    [16,  8, 14,  6]]) / 17.0

    # mask = np.asarray([[7, 9, 5],
    #                    [2, 1, 4],
    #                    [6, 3, 8]]) / 10.0

    # mask = np.asarray([[1, 3],
    #                    [4, 2]]) / 5.0

    h, w = image.shape[:2]
    reps = math.ceil(h / mask.shape[0]), math.ceil(w / mask.shape[1])

    mask = np.tile(mask, reps)[:h, :w] + 0.5
    mask = np.expand_dims(mask, -1)

    img_float = mask * image
    indexes = np.zeros((h, w), 'int')

    for y in range(h):
        for x in range(w):
            color = img_float[y, x]

            closest_idx, closest_color = get_closest(color, palette)

            img_float[y, x] = closest_color
            indexes[y, x] = closest_idx

    return img_float, indexes


def dither(image, palette, out=None, method='fs'):
    if method == 'fs':
        return floyd_steinberg(image, palette)
    elif method == 'ordered':
        return ordered(image, palette)
    else:
        raise Exception('Unknown method type \'%s\'' % str(method))


