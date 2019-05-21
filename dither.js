function dither(pix, width, height, palette) {
    var indexes = []

    var nextRowError = new Array((width + 1) * 4).fill(0);
    var nextPixError = new Array(3).fill(0);

    for (var y = 0; y < height; y += 1) {
        for (var x = 0; x < width; x += 1) {

            var r, g, b;
            var rc, gc, bc;

            [r, g, b] = at(pix, y, x, width);

            r += nextRowError[x * 4 + 0] + nextPixError[0];
            g += nextRowError[x * 4 + 1] + nextPixError[1];
            b += nextRowError[x * 4 + 2] + nextPixError[2];

            [rc, gc, bc, bi] = closest(r, g, b, palette);

            var re, ge, be;
            re = r - rc;
            ge = g - gc;
            be = b - bc;

            propagateError(nextPixError, 0, re, ge, be, 7 / 16);
            if (x > 0)
                propagateError(nextRowError, x * 4 + 0, re, ge, be, 3 / 16);
            propagateError(nextRowError, x * 4 + 1, re, ge, be, 5 / 16);
            propagateError(nextRowError, x * 4 + 2, re, ge, be, 1 / 16);

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

function propagateError(arr, index, re, ge, be, fraction) {
    arr[index + 0] = re * fraction;
    arr[index + 1] = ge * fraction;
    arr[index + 2] = be * fraction;
}