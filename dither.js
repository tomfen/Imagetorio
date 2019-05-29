function dither(pix, width, height, palette, method) {
    if (method == 'fs')
        return floydSteinberg(pix, width, height, palette);
    else if (method == 'closest')
        return quantize(pix, palette);
}

let a = 2.2;
let aInv = 1 / a;

function floydSteinberg(pix, width, height, palette) {
    
    var diffusionMatrix =
        [[0., 0., 7 / 16],
        [3 / 16, 5 / 16, 1 / 16]];

    return errorDiffusion(pix, width, height, palette, diffusionMatrix);
}

function reshape1darray(arr, d1, d2) {
    var newArr = [];

    var k = 0;

    for (var i = 0; i < d1; i++) {
        var row = []

        for (var j = 0; j < d2; j++) {

            var r = arr[k + 0] ** a;
            var g = arr[k + 1] ** a;
            var b = arr[k + 2] ** a;

            row.push([r, g, b]);

            k += 4;
        }

        newArr.push(row);
    }

    return newArr
}

function quantize(pix, palette) {
    var indexes = []

    for (var i = 0; i < pix.length; i += 4) {
        var r, g, b;
        var rc, gc, bc;

        r = pix[i];
        g = pix[i + 1];
        b = pix[i + 2];

        [rc, gc, bc, bi] = closest(r, g, b, palette);

        pix[i + 0] = rc
        pix[i + 1] = gc
        pix[i + 2] = bc

        indexes.push(bi)
    }

    return indexes
}

function gammaCorrect(palette) {
    var corected = [];
    for (var i = 0; i < palette.length; i++) {
        corected.push([
            palette[i][0] ** a,
            palette[i][1] ** a,
            palette[i][2] ** a]);
    }
    return corected;
}

function errorDiffusion(pix, width, height, palette, diffusionMatrix) {
    var indexes = [];
    var palette = gammaCorrect(palette);

    var mat = reshape1darray(pix, height, width);

    var diffusionOffset = diffusionMatrix[0].findIndex(val=>val != 0) - 1;

    for (var y = 0; y < height; y += 1) {
        for (var x = 0; x < width; x += 1) {

            var r, g, b;
            var rc, gc, bc;

            [r, g, b] = mat[y][x];

            [rc, gc, bc, bi] = closest(r, g, b, palette);

            var re, ge, be;
            re = r - rc;
            ge = g - gc;
            be = b - bc;

            for (var ye = 0; ye < diffusionMatrix.length; ye++) {
                var yImg = y + ye;
                if (yImg >= height) continue;

                for (var xe = 0; xe < diffusionMatrix[0].length; xe++) {
                    var xImg = x + xe - diffusionOffset;
                    if (xImg < 0 || width <= xImg) continue;
                    propagateError(mat[yImg][xImg], re, ge, be, diffusionMatrix[ye][xe]);
                }
            }

            setPix(pix, y, x, width, rc ** aInv, gc ** aInv, bc ** aInv);
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
    var bestDistance = Infinity;

    for (var i = 0; i < palette.length; i += 1) {

        var [rp, gp, bp] = palette[i];
        var distance = colorDistance(r, g, b, rp, gp, bp)

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

function propagateError(arr, re, ge, be, fraction) {
    arr[0] += re * fraction;
    arr[1] += ge * fraction;
    arr[2] += be * fraction;
}

function colorDistance(r1, g1, b1, r2, g2, b2) {
    var rd, gd, bd;
    rd = r1 - r2;
    gd = g1 - g2;
    bd = b1 - b2;

    return rd * rd + gd * gd + bd * bd;
}