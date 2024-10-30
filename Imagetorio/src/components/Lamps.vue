<template>
  <v-container>
    <v-row>
      <v-col>
        <v-img
          :src="imageUrl"
          max-height="500px"
          ref="image"
          @load="imageLoaded"
        />
      </v-col>
      <v-col>
        <canvas
          ref="canvas"
          style="
            height: 100%;
            max-height: 500px;
            max-width: 100%;
            image-rendering: pixelated;
          "
        ></canvas>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-file-input
          type="file"
          class="input"
          label="Upload file"
          outlined
          dense
          @update:model-value="onFileChange"
        />
      </v-col>
      <v-col>
        <SizeSelect
          :originalDimensions="originalDimensions"
          v-model="dimensions"
        />
      </v-col>
      <v-col>
        <BlueprintBox
          @generate="generateBlueprint"
          :content="blueprint"
        ></BlueprintBox>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import BlueprintBox from "./BlueprintBox.vue";
import SizeSelect from "./SizeSelect.vue";

import { parseGIF, decompressFrames } from "gifuct-js";
import pako from "pako";

import { exportBlueprint } from "@/scripts/blueprint";
import { generateLampImage } from "@/scripts/generateLamps";

export default {
  data() {
    return {
      imageUrl: "",
      frames: null,
      width: 50,
      height: 50,
      blueprint: "",
      dimensions: { width: 100, height: 100 },
      originalDimensions: { width: null, height: null },
      imageData: null,
    };
  },
  watch: {
    imageUrl(value) {
      // var promisedGif = fetch(value)
      //   .then((resp) => resp.arrayBuffer())
      //   .then((buff) => {
      //     var gif = parseGIF(buff);
      //     this.frames = decompressFrames(gif, true);
      //   });
    },
    frames(value) {
      console.log(value);
    },
    "dimensions.height"(value) {
      this.generate();
    },
    "dimensions.width"(value) {
      this.generate();
    },
  },
  computed: {
    isGif() {
      let mime = this.imageUrl.substring(
        this.imageUrl.indexOf(":") + 1,
        this.imageUrl.indexOf(";")
      );
      return mime === "image/gif";
    },
  },
  methods: {
    imageLoaded() {
      this.originalDimensions = {
        height: this.$refs.image.naturalHeight,
        width: this.$refs.image.naturalWidth,
      };
    },
    createImage(file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        this.imageUrl = e.target.result;
      };
      reader.readAsDataURL(file);
    },
    onFileChange(file) {
      if (!file) {
        return;
      }

      this.createImage(file);
    },
    async generate() {
      if (!this.imageUrl) return;

      if (this.isGif) {
        // TODO
      } else {
        this.generateStatic();
      }
    },
    async generateStatic() {
      let canvas = this.$refs.canvas;

      canvas.height = this.dimensions.height;
      canvas.width = this.dimensions.width;

      let ctx = canvas.getContext("2d");

      let image = new Image();

      await new Promise((r) => (image.onload = r), (image.src = this.imageUrl));

      ctx.drawImage(image, 0, 0, this.dimensions.width, this.dimensions.height);

      let data = ctx.getImageData(
        0,
        0,
        this.dimensions.width,
        this.dimensions.height
      );
      this.imageData = data;
    },

    generateBlueprint() {
      let bp = generateLampImage(
        this.imageData.data,
        Number(this.dimensions.width),
        Number(this.dimensions.height)
      );

      this.blueprint = exportBlueprint(bp);
    },
  },
  components: { SizeSelect },
};
</script>
