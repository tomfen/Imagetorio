function dither(pix, width, height, palette) {
    var indexes = []

    for (var y = 0; y < height; y += 1) {
        for (var x = 0; x < width; x += 1) {

            var r, g, b;
            var rc, gc, bc;

            [r, g, b] = at(pix, y, x, width);

            [rc, gc, bc, bi] = closest(r, g, b, palette);

            var re, ge, be;
            re = rc - r;
            ge = gc - g;
            be = bc - b;

            if (x < height - 1) {
                propagateError(pix, y, x + 1, width, re, ge, be, 7 / 16);
            }

            if (y < height - 1) {
                if (x > 0) {
                    propagateError(pix, y + 1, x - 1, width, re, ge, be, 3 / 16);
                }

                propagateError(pix, y + 1, x, width, re, ge, be, 5 / 16);

                if (x < height - 1) {
                    propagateError(pix, y + 1, x + 1, width, re, ge, be, 1 / 16);
                }
            }

            setPix(pix, y, x, width, rc, gc, bc);
            indexes.push(bi)
        }
    }

    return indexes
}


function at(pix, y, x, width) {
    index = (y * width + x) * 4;

    var r, g, b;
    r = pix[index];
    g = pix[index + 1];
    b = pix[index + 2];
    return [r, g, b]
}

function setPix(pix, y, x, width, r, g, b) {
    index = (y * width + x) * 4;

    pix[index] = r;
    pix[index + 1] = g;
    pix[index + 2] = b;
}

function closest(r, g, b, palette) {

    var rc, gc, bc;
    var ic = 0;
    var bestDistance = 999999;

    for (var i = 0; i < palette.length; i += 1) {

        var [rp, gp, bp] = palette[i];
        var rd = rp - r;
        var gd = gp - g;
        var bd = bp - b;

        var distance = rd * rd + gd * gd + bd * bd;

        if (distance < bestDistance) {
            ic = i;
            bestDistance = distance;
            rc = rp;
            gc = gp;
            bc = bp;
        }
    }

    return [rc, gc, bc, ic];
}

function propagateError(pix, y, x, width, r, g, b, fraction) {
    index = (y * width + x) * 4;

    pix[index] -= r * fraction;
    pix[index + 1] -= g * fraction;
    pix[index + 2] -= b * fraction;
}