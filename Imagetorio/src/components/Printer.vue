<template>
  <v-container>
    <v-row>
      <v-col>
        <div class="previewBox">
          <canvas id="canvas1" class="preview"></canvas>
          <canvas id="canvas2" class="preview"></canvas>
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <input type="file" id="imgfile" @input="loadImage" />
      </v-col>
    </v-row>
    <v-row>
      <v-col class="shrink">
        <v-slider
          label="Brightness"
          width="500"
          min="-255"
          max="255"
          show-ticks="always"
          :ticks="{ '-255': '-255', '-27': 'N', 0: '0', 255: '255' }"
          v-model="brightness"
        />

        <v-slider
          label="Contrast"
          width="500"
          min="0"
          max="2"
          show-ticks="always"
          :ticks="{ 0: '0', '0.62': 'N', 1: '1', 2: '2' }"
          v-model="contrast"
        />
      </v-col>
      <v-col class="shrink">
        <v-text-field
          v-model="imgheight"
          variant="outlined"
          label="Max height"
          min="1"
          max="1000"
          max-width="100"
          density="compact"
          type="number"
        />
        <v-text-field
          v-model="imgwidth"
          variant="outlined"
          label="Max width"
          min="1"
          max="1000"
          max-width="100"
          density="compact"
          type="number"
        />
      </v-col>
      <v-col class="shrink">
        <BlueprintBox
          :content="blueprintString"
          @generate="getBlueprint"
          @copy="copyBlueprint"
        />
      </v-col>
      <v-spacer></v-spacer>
    </v-row>

    <v-row>
      <v-col class="shrink">
        <DirectionRadio v-model="direction" />
      </v-col>
      <v-col class="shrink">
        <v-checkbox v-model="ditherChecked" label="dither" />
      </v-col>
      <VSpacer></VSpacer>
    </v-row>
    <ItemSelect
      :itemCount="itemCount"
      v-model="selectedItems"
      @update:palette="
        (v) => {
          palette = v;
        }
      "
    />
  </v-container>
  <v-snackbar timeout="2000" v-model="snackbar">
    Copied to clipboard
  </v-snackbar>
</template>

<script>
import BlueprintBox from "@/components/BlueprintBox.vue";
import DirectionRadio from "@/components/DirectionRadio.vue";
import ItemSelect from "@/components/ItemSelect.vue";

import pako from "pako";

let a = 2.2;
let aInv = 1 / a;

var idx, img;

var Direction = {
  N: 0,
  E: 2,
  S: 4,
  W: 6,
};

export default {
  data() {
    return {
      direction: "e",
      blueprintString: "",

      ditherChecked: true,
      imgheight: 100,
      imgwidth: 100,
      contrast: 1,
      brightness: 0,

      selectedItems: [],
      palette: [],

      itemCount: {},

      snackbar: false,
      widthTemp: null,
    };
  },
  watch: {
    ditherChecked() {
      this.refreshDithered();
    },
    imgheight() {
      this.refreshDithered();
    },
    imgwidth() {
      this.refreshDithered();
    },
    palette() {
      this.refreshDithered();
    },
    contrast() {
      this.refreshPreview();
    },
    brightness() {
      this.refreshPreview();
    },
    direction() {
      this.refreshPreview();
    },
  },
  components: {
    DirectionRadio,
    ItemSelect,
    BlueprintBox,
  },
  methods: {
    loadImage() {
      let input = document.getElementById("imgfile");

      let file = input.files[0];
      let fr = new FileReader();

      let createImage = () => {
        img = new Image();
        img.onload = this.imageLoaded;
        img.src = fr.result;
      };

      fr.onload = createImage;
      fr.readAsDataURL(file);
    },
    imageLoaded() {
      var canvas = document.getElementById("canvas1");

      var [cnvW, cnvH] = this.clipSize(img.width, img.height, 500, 1000);

      canvas.width = cnvW;
      canvas.height = cnvH;

      this.refreshPreview();
    },
    refreshPreview() {
      if (!img) return;

      var canvas = document.getElementById("canvas1");
      var ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      var imgd = ctx.getImageData(0, 0, canvas.width, canvas.height);

      this.adjust(imgd);

      ctx.putImageData(imgd, 0, 0);

      this.refreshDithered();
    },
    dither(pix, width, height, palette, method) {
      if (method == "fs") {
        return this.floydSteinberg(pix, width, height, palette);
      } else if (method == "closest") {
        return this.quantize(pix, palette);
      }
    },
    floydSteinberg(pix, width, height, palette) {
      var diffusionMatrix = [
        [0, 0, 7 / 16],
        [3 / 16, 5 / 16, 1 / 16],
      ];

      return this.errorDiffusion(pix, width, height, palette, diffusionMatrix);
    },
    reshape1darray(arr, d1, d2) {
      var newArr = [];

      var k = 0;

      for (var i = 0; i < d1; i++) {
        var col = [];

        for (var j = 0; j < d2; j++) {
          var r = arr[k + 0] ** a;
          var g = arr[k + 1] ** a;
          var b = arr[k + 2] ** a;

          col.push([r, g, b]);

          k += 4;
        }

        newArr.push(col);
      }

      return newArr;
    },
    quantize(pix, palette) {
      var indexes = [];

      let closest = this.closest;

      for (var i = 0; i < pix.length; i += 4) {
        var r, g, b;
        var rc, gc, bc, bi;

        r = pix[i];
        g = pix[i + 1];
        b = pix[i + 2];

        [rc, gc, bc, bi] = closest(r, g, b, palette);

        pix[i + 0] = rc;
        pix[i + 1] = gc;
        pix[i + 2] = bc;

        indexes.push(bi);
      }

      return indexes;
    },
    gammaCorrect(palette) {
      var corected = [];
      for (var i = 0; i < palette.length; i++) {
        corected.push([
          palette[i][0] ** a,
          palette[i][1] ** a,
          palette[i][2] ** a,
        ]);
      }
      return corected;
    },
    errorDiffusion(pix, width, height, palette2, diffusionMatrix) {
      var indexes = [];
      var palette = this.gammaCorrect(palette2);

      var mat = this.reshape1darray(pix, height, width);

      var diffusionOffset = diffusionMatrix[0].findIndex((val) => val != 0) - 1;

      let closest = this.closest;

      for (var y = 0; y < height; y += 1) {
        for (var x = 0; x < width; x += 1) {
          var r, g, b;
          var rc, gc, bc, bi;

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
              this.propagateError(
                mat[yImg][xImg],
                re,
                ge,
                be,
                diffusionMatrix[ye][xe]
              );
            }
          }

          this.setPix(pix, y, x, width, rc ** aInv, gc ** aInv, bc ** aInv);
          indexes.push(bi);
        }
      }

      return indexes;
    },
    at(pix, y, x, width) {
      let index = (y * width + x) * 4;

      var r, g, b;
      r = pix[index];
      g = pix[index + 1];
      b = pix[index + 2];
      return [r, g, b];
    },
    setPix(pix, y, x, width, r, g, b) {
      let index = (y * width + x) * 4;

      pix[index] = r;
      pix[index + 1] = g;
      pix[index + 2] = b;
    },
    closest(r, g, b, palette) {
      var rc, gc, bc;
      var ic = 0;
      var bestDistance = Infinity;

      let colorDistance = this.colorDistance;

      for (var i = 0; i < palette.length; i += 1) {
        var [rp, gp, bp] = palette[i];
        var distance = colorDistance(r, g, b, rp, gp, bp);

        if (distance < bestDistance) {
          ic = i;
          bestDistance = distance;
          rc = rp;
          gc = gp;
          bc = bp;
        }
      }

      return [rc, gc, bc, ic];
    },
    propagateError(arr, re, ge, be, fraction) {
      arr[0] += re * fraction;
      arr[1] += ge * fraction;
      arr[2] += be * fraction;
    },
    colorDistance(r1, g1, b1, r2, g2, b2) {
      var rd, gd, bd;
      rd = r1 - r2;
      gd = g1 - g2;
      bd = b1 - b2;

      return rd * rd + gd * gd + bd * bd;
    },
    makePrinter(idx, width, direction, items) {
      let blueprint = {
        blueprint: {
          entities: [],
          icons: [],
          item: "blueprint",
          version: 73016672256,
        },
      };

      var idxMatrix = this.reshape(idx, width);

      var stripes = this.getStripes(idxMatrix, direction);

      var counter = {
        i: -1,
        next: function () {
          return ++this.i;
        },
        last: function () {
          return this.i;
        },
      };

      var onSwitch = this.put_switch(blueprint, counter);
      var multiplierHook = onSwitch;

      for (var x = 0; x < stripes.length; x++) {
        let stripe = stripes[x];

        this.put_canvas(
          blueprint,
          counter,
          x,
          -1,
          Math.floor(stripe.length / 8)
        );
        this.put_splitter(blueprint, counter, x, 0);
        var [multiplier, divider, bit_shifter] = this.put_decoder(
          blueprint,
          counter,
          x,
          7
        );
        this.put_memory(
          blueprint,
          counter,
          x,
          32,
          divider,
          bit_shifter,
          stripe,
          items
        );

        this.connect("red", multiplier, multiplierHook, 1, 1);
        multiplierHook = multiplier;
      }

      this.rotateToTargetDirection(blueprint, direction);

      return this.exportBlueprint(blueprint);
    },
    put_switch(blueprint, counter) {
      var onSwitch = {
        entity_number: counter.next(),
        name: "constant-combinator",
        position: { x: -1, y: 12 },
        direction: Direction.E,
        control_behavior: {
          filters: [
            {
              signal: { type: "virtual", name: "signal-S" },
              count: 0,
              index: 1,
            },
            {
              signal: { type: "virtual", name: "signal-W" },
              count: 0,
              index: 2,
            },
            {
              signal: { type: "virtual", name: "signal-I" },
              count: 0,
              index: 3,
            },
            {
              signal: { type: "virtual", name: "signal-T" },
              count: 0,
              index: 4,
            },
            {
              signal: { type: "virtual", name: "signal-C" },
              count: 0,
              index: 5,
            },
            {
              signal: { type: "virtual", name: "signal-H" },
              count: 0,
              index: 6,
            },
            {
              signal: { type: "virtual", name: "signal-O" },
              count: 5,
              index: 7,
            },
            {
              signal: { type: "virtual", name: "signal-N" },
              count: 0,
              index: 8,
            },
            {
              signal: { type: "virtual", name: "signal-red" },
              count: -1,
              index: 17,
            },
            {
              signal: { type: "virtual", name: "signal-green" },
              count: 1,
              index: 18,
            },
          ],
          is_on: false,
        },
      };

      blueprint["blueprint"]["entities"].push(onSwitch);

      var lamp = {
        entity_number: counter.next(),
        name: "small-lamp",
        position: { x: -1, y: 13 },
        control_behavior: {
          circuit_condition: {
            first_signal: { type: "virtual", name: "signal-anything" },
            constant: 0,
            comparator: ">",
          },
          use_colors: true,
        },
      };

      blueprint["blueprint"]["entities"].push(lamp);

      var redConstant = {
        entity_number: counter.next(),
        name: "constant-combinator",
        position: { x: 1, y: 14 },
        control_behavior: {
          filters: [
            {
              signal: { type: "virtual", name: "signal-red" },
              count: 1,
              index: 1,
            },
          ],
        },
      };

      blueprint["blueprint"]["entities"].push(redConstant);

      this.connect("red", redConstant, lamp);
      this.connect("red", onSwitch, lamp);

      return onSwitch;
    },
    rotateToTargetDirection(blueprint, direction) {
      switch (direction) {
        case "s":
          /*do nothing*/ break;
        case "w":
          this.rotateRight(blueprint, 1);
          break;
        case "n":
          this.rotateRight(blueprint, 2);
          break;
        case "e":
          this.rotateRight(blueprint, 3);
          break;
      }
    },
    rotateRight(blueprint, rotations) {
      rotations = this.mod(rotations, 4);

      var entities = blueprint["blueprint"]["entities"];

      if (rotations == 0) return;

      var transformMatrix =
        rotations == 1
          ? [
              [0, -1],
              [1, 0],
            ]
          : rotations == 2
          ? [
              [-1, 0],
              [0, -1],
            ]
          : [
              [0, 1],
              [-1, 0],
            ];

      entities.forEach((entity) => {
        var currentPos = entity.position;
        var newPos = {};
        newPos.x =
          transformMatrix[0][0] * currentPos.x +
          transformMatrix[0][1] * currentPos.y;
        newPos.y =
          transformMatrix[1][0] * currentPos.x +
          transformMatrix[1][1] * currentPos.y;
        entity.position = newPos;

        if ("direction" in entity) {
          entity.direction = this.mod(entity.direction + rotations * 2, 8);
        } else {
          entity.direction = this.mod(Direction.N + rotations * 2, 8);
        }
      });
    },
    mod(n, m) {
      return ((n % m) + m) % m;
    },
    exportBlueprint(obj) {
      var string = JSON.stringify(obj);
      var binaryString = pako.deflate(string, { to: "string" });
      var base64 = btoa(binaryString);
      return "0" + base64;
    },
    getStripes(idx, direction) {
      var height = idx.length;
      var width = idx[0].length;

      let stripes = [];

      switch (direction) {
        case "n":
          for (let x = width - 2; x >= 0; x -= 2) {
            let stripe = [];

            for (let y = height - 1; y >= 0; y--) {
              stripe.push(idx[y][x]);
              stripe.push(idx[y][x + 1]);
            }

            stripes.push(stripe);
          }
          break;

        case "w":
          for (let y = 0; y < height; y += 2) {
            let stripe = [];

            for (let x = width - 1; x >= 0; x--) {
              stripe.push(idx[y + 1][x]);
              stripe.push(idx[y][x]);
            }

            stripes.push(stripe);
          }
          break;

        case "s":
          for (let x = 0; x < width; x += 2) {
            let stripe = [];

            for (let y = 0; y < height; y++) {
              stripe.push(idx[y][x + 1]);
              stripe.push(idx[y][x]);
            }

            stripes.push(stripe);
          }
          break;

        case "e":
          for (let y = height - 2; y >= 0; y -= 2) {
            let stripe = [];

            for (let x = 0; x < width; x++) {
              stripe.push(idx[y][x]);
              stripe.push(idx[y + 1][x]);
            }

            stripes.push(stripe);
          }
          break;
      }

      return stripes;
    },
    reshape(arr, newWidth) {
      var copy = [...arr];
      var newArr = [];
      while (copy.length) newArr.push(copy.splice(0, newWidth));

      return newArr;
    },
    put_canvas(blueprint, counter, x, y, length) {
      for (var i = 0; i < length; i++) {
        let belt = {
          entity_number: counter.next(),
          name: "express-transport-belt",
          position: { x: x, y: y - i },
        };
        blueprint["blueprint"]["entities"].push(belt);
      }
    },
    put_splitter(blueprint, counter, x, y) {
      const UNDR = "express-underground-belt";
      const BELT = "express-transport-belt";
      const SPLT = "express-splitter";

      var entities;
      if (x % 2 == 0) {
        entities = [
          {
            entity_number: counter.next(),
            name: UNDR,
            position: { x: x, y: y },
            direction: Direction.N,
            type: "output",
          },
          {
            entity_number: counter.next(),
            name: BELT,
            position: { x: x - 1, y: y + 4 },
            direction: Direction.E,
          },
          {
            entity_number: counter.next(),
            name: UNDR,
            position: { x: x, y: y + 3 },
            type: "input",
          },
          {
            entity_number: counter.next(),
            name: BELT,
            position: { x: x, y: y + 4 },
          },
          {
            entity_number: counter.next(),
            name: BELT,
            position: { x: x, y: y + 6 },
          },
          {
            entity_number: counter.next(),
            name: SPLT,
            position: { x: x - 0.5, y: y + 5 },
          },
        ];
      } else {
        entities = [
          {
            entity_number: counter.next(),
            name: BELT,
            position: { x: x, y: y },
          },
          {
            entity_number: counter.next(),
            name: SPLT,
            position: { x: x - 0.5, y: y + 2 },
          },
          {
            entity_number: counter.next(),
            name: BELT,
            position: { x: x - 1, y: y + 1 },
            direction: Direction.E,
          },
          {
            entity_number: counter.next(),
            name: BELT,
            position: { x: x, y: y + 1 },
          },
          {
            entity_number: counter.next(),
            name: UNDR,
            position: { x: x, y: y + 3 },
            type: "output",
          },
          {
            entity_number: counter.next(),
            name: UNDR,
            position: { x: x, y: y + 6 },
            type: "input",
          },
        ];
      }

      entities.forEach((entity) => {
        blueprint["blueprint"]["entities"].push(entity);
      });
    },
    connect(wire, first, second, first_circuit = 1, second_circuit = 1) {
      var ent2id = second["entity_number"];

      if (!("connections" in first)) {
        first["connections"] = {};
      }

      if (!(first_circuit in first["connections"])) {
        first["connections"][first_circuit] = {};
      }

      if (!(wire in first["connections"][first_circuit])) {
        first["connections"][first_circuit][wire] = [];
      }

      first["connections"][first_circuit][wire].push({
        entity_id: ent2id,
        circuit_id: second_circuit,
      });
    },
    put_decoder(blueprint, counter, x, y) {
      blueprint["blueprint"]["entities"].push({
        entity_number: counter.next(),
        name: "express-underground-belt",
        position: { x: x, y: y },
        type: "output",
      });
      blueprint["blueprint"]["entities"].push({
        entity_number: counter.next(),
        name: "express-underground-belt",
        position: { x: x, y: y + 8 },
        type: "input",
      });

      let requester = {
        entity_number: counter.next(),
        name: "logistic-chest-requester",
        position: { x: x, y: y + 10 },
        control_behavior: { circuit_mode_of_operation: 1 },
      };

      let multiplier = {
        entity_number: counter.next(),
        name: "arithmetic-combinator",
        position: { x: x, y: y + 5.5 },
        direction: Direction.S,
        control_behavior: {
          arithmetic_conditions: {
            first_signal: { type: "virtual", name: "signal-each" },
            second_signal: { type: "virtual", name: "signal-O" },
            operation: "*",
            output_signal: { type: "virtual", name: "signal-each" },
          },
        },
      };

      let inserter = {
        entity_number: counter.next(),
        name: "stack-filter-inserter",
        position: { x: x, y: y + 9 },
        direction: Direction.S,
        control_behavior: {
          circuit_mode_of_operation: 1,
          circuit_read_hand_contents: true,
        },
        override_stack_size: 1,
      };

      let cleaner = {
        entity_number: counter.next(),
        name: "stack-filter-inserter",
        position: { x: x, y: y + 11 },
        direction: Direction.N,
        control_behavior: {
          circuit_mode_of_operation: 1,
        },
        filter_mode: "blacklist",
        override_stack_size: 1,
      };

      let trash = {
        entity_number: counter.next(),
        name: "logistic-chest-passive-provider",
        position: { x: x, y: y + 12 },
      };

      let pulse_conv = {
        entity_number: counter.next(),
        name: "decider-combinator",
        position: { x: x, y: y + 14.5 },
        direction: Direction.S,
        control_behavior: {
          decider_conditions: {
            first_signal: { type: "virtual", name: "signal-anything" },
            constant: 0,
            comparator: ">",
            output_signal: { type: "virtual", name: "signal-I" },
            copy_count_from_input: false,
          },
        },
      };
      let bit_shifter = {
        entity_number: counter.next(),
        name: "arithmetic-combinator",
        position: { x: x, y: y + 20.5 },
        direction: Direction.N,
        control_behavior: {
          arithmetic_conditions: {
            first_signal: { type: "virtual", name: "signal-each" },
            second_signal: { type: "virtual", name: "signal-I" },
            operation: ">>",
            output_signal: { type: "virtual", name: "signal-each" },
          },
        },
      };

      let bit_and = {
        entity_number: counter.next(),
        name: "arithmetic-combinator",
        position: { x: x, y: y + 18.5 },
        direction: Direction.N,
        control_behavior: {
          arithmetic_conditions: {
            first_signal: { type: "virtual", name: "signal-each" },
            second_constant: 1,
            operation: "AND",
            output_signal: { type: "virtual", name: "signal-each" },
          },
        },
      };

      let it_counter = {
        entity_number: counter.next(),
        name: "arithmetic-combinator",
        position: { x: x, y: y + 16.5 },
        direction: Direction.S,
        control_behavior: {
          arithmetic_conditions: {
            first_signal: { type: "virtual", name: "signal-I" },
            second_constant: 1,
            operation: "*",
            output_signal: { type: "virtual", name: "signal-I" },
          },
        },
      };

      let divider = {
        entity_number: counter.next(),
        name: "arithmetic-combinator",
        position: { x: x, y: y + 23.5 },
        direction: Direction.S,
        control_behavior: {
          arithmetic_conditions: {
            first_signal: { type: "virtual", name: "signal-I" },
            second_constant: 32,
            operation: "/",
            output_signal: { type: "virtual", name: "signal-G" },
          },
        },
      };

      this.connect("green", multiplier, requester, 2);
      this.connect("green", inserter, multiplier, 1);
      this.connect("green", inserter, cleaner);
      this.connect("red", pulse_conv, inserter, 1);
      this.connect("red", bit_shifter, it_counter, 1, 2);
      this.connect("red", bit_shifter, divider, 1, 1);
      this.connect("green", bit_shifter, bit_and, 2, 1);
      this.connect("green", bit_and, inserter, 2);
      this.connect("green", it_counter, it_counter, 1, 2);
      this.connect("red", it_counter, pulse_conv, 1, 2);

      let entities = [
        requester,
        multiplier,
        inserter,
        cleaner,
        trash,
        pulse_conv,
        bit_shifter,
        bit_and,
        it_counter,
        divider,
      ];

      entities.forEach((entity) => {
        blueprint["blueprint"]["entities"].push(entity);
      });

      if (x % 7 == 0) {
        [y + 7, y + 13, y + 22].forEach((_y) => {
          let pole = {
            entity_number: counter.next(),
            name: "medium-electric-pole",
            position: { x: x, y: _y },
          };

          blueprint["blueprint"]["entities"].push(pole);
        });
      }

      if (x % 4 == 0) {
        let roboport = {
          entity_number: counter.next(),
          name: "roboport",
          position: { x: x + 1.5, y: y + 2.5 },
        };
        blueprint["blueprint"]["entities"].push(roboport);
      }

      return [multiplier, divider, bit_shifter];
    },
    bit_vector_to_int(arr) {
      var ret = 0;

      for (var i = 0; i < arr.length; i++) {
        ret |= arr[i] << i;
      }

      return ret;
    },
    put_memory(
      blueprint,
      counter,
      x,
      entity_y,
      divider,
      bit_shifter,
      id_list,
      names
    ) {
      function onlyUnique(value, index, self) {
        return self.indexOf(value) === index;
      }
      for (var i = 0; i < id_list.length; i += 32) {
        var strip = id_list.slice(i, i + 32);
        var strip_number = Math.floor(i / 32);

        var filters = [];

        var unique = strip.filter(onlyUnique);

        unique.forEach((item_idx) => {
          var item = names[item_idx];

          var item_bit_vector = strip.map((v) => {
            if (v == item_idx) return 1;
            else return 0;
          });

          var integer = this.bit_vector_to_int(item_bit_vector);

          filters.push({
            count: integer,
            index: (filters.length % 18) + 1,
            signal: { type: "item", name: item },
          });
        });

        var decider_connections;
        if (strip_number == 0) {
          decider_connections = {
            1: {
              red: [
                {
                  entity_id: divider["entity_number"],
                  circuit_id: 2,
                },
              ],
            },
            2: {
              green: [
                {
                  entity_id: bit_shifter["entity_number"],
                  circuit_id: 1,
                },
              ],
            },
          };
        } else {
          decider_connections = {
            1: {
              red: [
                {
                  entity_id: decider_combinator["entity_number"],
                  circuit_id: 1,
                },
              ],
            },
            2: {
              green: [
                {
                  entity_id: decider_combinator["entity_number"],
                  circuit_id: 2,
                },
              ],
            },
          };
        }
        var decider_combinator = {
          connections: decider_connections,
          control_behavior: {
            decider_conditions: {
              first_signal: { type: "virtual", name: "signal-G" },
              constant: strip_number,
              comparator: "=",
              output_signal: { type: "virtual", name: "signal-everything" },
              copy_count_from_input: "true",
            },
          },
          direction: Direction.N,
          entity_number: counter.next(),
          name: "decider-combinator",
          position: { x: x, y: entity_y + 0.5 },
        };

        var constant_combinator1 = {
          connections: {
            1: {
              green: [
                {
                  entity_id: counter.last(),
                  circuit_id: 1,
                },
              ],
            },
          },
          control_behavior: { filters: filters.slice(0, 18) },
          entity_number: counter.next(),
          name: "constant-combinator",
          position: { x: x, y: entity_y + 2 },
        };

        blueprint["blueprint"]["entities"].push(decider_combinator);
        blueprint["blueprint"]["entities"].push(constant_combinator1);

        if (filters.length > 18) {
          let constant_combinator2 = {
            connections: {
              1: {
                green: [
                  {
                    entity_id: counter.last(),
                    circuit_id: 1,
                  },
                ],
              },
            },
            control_behavior: { filters: filters.slice(18) },
            entity_number: counter.next(),
            name: "constant-combinator",
            position: { x: x, y: entity_y + 3 },
          };
          entity_y += 1;

          blueprint["blueprint"]["entities"].push(constant_combinator2);
        }

        if ((x + strip_number * 3) % 7 == 0) {
          let pole = {
            entity_number: counter.next(),
            name: "medium-electric-pole",
            position: { x: x, y: entity_y + 3 },
          };

          blueprint["blueprint"]["entities"].push(pole);
          entity_y += 1;
        }

        entity_y += 3;
      }
    },

    getSize(img) {
      var wMax = this.imgwidth;
      var hMax = this.imgheight;

      var [w, h] = this.clipSize(img.width, img.height, wMax, hMax);

      if (this.isVertical()) {
        w *= 2;
        h *= 4;
      } else {
        w *= 4;
        h *= 2;
      }
      return [w, h];
    },
    clipSize(w, h, wMax, hMax) {
      if (w < wMax && h < hMax) {
        return [w, h];
      }

      let hRatio = wMax / w;
      let vRatio = hMax / h;

      if (vRatio < hRatio) {
        w = Math.ceil(w * vRatio);
        h = hMax;
      } else {
        w = wMax;
        h = Math.ceil(h * hRatio);
      }

      return [w, h];
    },
    drawDithered(imagedata, ctx, width, height) {
      var tempCanvas = document.createElement("canvas");
      var tempCtx = tempCanvas.getContext("2d");

      tempCanvas.width = imagedata.width;
      tempCanvas.height = imagedata.height;

      tempCtx.putImageData(imagedata, 0, 0);

      var img = new Image();
      img.onload = function () {
        ctx.imageSmoothingEnabled = false;
        ctx.drawImage(img, 0, 0, width, height);
      };
      img.src = tempCanvas.toDataURL();
    },
    refreshDithered() {
      if (!img) return;

      console.time("Preview gen");

      var canvas = document.getElementById("canvas1");
      var canvas2 = document.getElementById("canvas2");

      canvas2.width = canvas.width;
      canvas2.height = canvas.height;

      var ctx2 = canvas2.getContext("2d");

      let [w, h] = this.getSize(img);

      var imgd = this.resize(img, w, h);
      var pix = imgd.data;

      var method = this.ditherChecked ? "fs" : "closest";

      this.widthTemp = w;

      console.time("Dither");
      idx = this.dither(
        pix,
        w,
        h,
        JSON.parse(JSON.stringify(this.palette)),
        method
      );
      console.timeEnd("Dither");

      this.drawDithered(imgd, ctx2, canvas.width, canvas.height);

      this.updateRequirements(idx);

      console.timeEnd("Preview gen");
    },
    adjust(imgd) {
      var contrast = this.contrast;
      var brightness = this.brightness;

      var data = imgd.data;
      for (var i = 0; i < data.length; i += 4) {
        data[i + 0] = contrast * (data[i + 0] - 128) + 128 + brightness;
        data[i + 1] = contrast * (data[i + 1] - 128) + 128 + brightness;
        data[i + 2] = contrast * (data[i + 2] - 128) + 128 + brightness;
      }
    },
    resize(img, width, height) {
      var canvas = document.createElement("canvas");
      var ctx = canvas.getContext("2d");

      canvas.height = height;
      canvas.width = width;

      ctx.drawImage(img, 0, 0, width, height);

      var imgd = ctx.getImageData(0, 0, width, height);

      this.adjust(imgd);

      return imgd;
    },
    getBlueprint() {
      this.blueprintString = this.makePrinter(
        idx,
        this.widthTemp, // TODO:FIXME
        this.direction,
        this.getNames()
      );
    },
    isVertical() {
      var v = this.direction;
      return v == "n" || v == "s";
    },
    getPalette() {
      return this.palette;
    },

    getNames() {
      return this.selectedItems;
    },
    updateRequirements(idx) {
      var names = this.getNames();

      let counts = {};

      for (var i = 0; i < names.length; i++) {
        var name = names[i];

        let count = 0;

        for (let pxl of idx) {
          if (pxl == i) count++;
        }

        counts[name] = count;
      }

      this.itemCount = counts;
    },
    copyBlueprint() {
      var bp = document.getElementById("blueprint");

      bp.focus();
      bp.select();

      document.execCommand("copy");

      this.snackbar = true;
    },
  },
};
</script>

<style scoped lang="css">
div.previewBox {
  float: left;
}

.preview {
  border: 1px solid rgb(97, 97, 97);
  background: rgb(236, 236, 236);
}
</style>
