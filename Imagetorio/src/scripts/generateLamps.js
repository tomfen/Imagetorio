export function generateLampImage(imageData, width, height) {
  let entities = [];
  let wires = [];

  const POWER = 5;

  const range = 28;
  let i = 1;

  for (let y = -1; y < height + range/2; y += range) {
    for (let x = -1; x < width + range/2; x += range) {
      let substation = {
        entity_number: i,
        name: "substation",
        quality: "legendary",
        position: {
          x: x,
          y: y,
        },
      };

      entities.push(substation);
      if (x != -1) {
        wires.push([i - 1, POWER, i, POWER]);
      }

      i++;
    }
  }

  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if ((x + 2) % range <= 1 && (y + 2) % range <= 1) {
        continue;
      }

      let r = imageData[(x + y * width) * 4 + 0];
      let g = imageData[(x + y * width) * 4 + 1];
      let b = imageData[(x + y * width) * 4 + 2];

      let lamp = {
        entity_number: i++,
        name: "small-lamp",
        position: {
          x: 0.5 + x,
          y: 0.5 + y,
        },
        color: {
          r: r / 255,
          g: g / 255,
          b: b / 255,
          a: 1,
        },
        always_on: true,
      };

      entities.push(lamp);
    }
  }

  let bp = {
    blueprint: {
      icons: [
        {
          signal: {
            name: "small-lamp",
          },
          index: 1,
        },
      ],
      entities: entities,
      wires: wires,
      item: "blueprint",
      label: "TODO",
      version: 562949954207746,
    },
  };

  return bp;
}
