import numpy as np


def distance(c1, c2):
    return np.linalg.norm(c1-c2, 2)


def get_closest(color, palette):
    closest_idx, closest_color = min((x for x in enumerate(palette)), key=lambda x: distance(x[1], color))

    return closest_idx, closest_color


def dither(image, palette, out=None, method=None):

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

            if x < width-1:
                img_float[y][x+1] += error * 7/16

            if y < height-1:
                if 0 < x:
                    img_float[y+1][x-1] += error * 3/16

                img_float[y+1][x] += error * 5/16

                if x < width-1:
                    img_float[y+1][x+1] += error * 1/16

    return dithered, indexes
