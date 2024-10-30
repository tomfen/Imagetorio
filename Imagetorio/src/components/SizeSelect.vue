<template>
  <div class="d-flex">
    <div
      class="d-flex"
      style="
        flex-direction: column;
        padding: 10px 0;
        margin-right: 3px;
        align-items: center;
      "
    >
      <div class="lock-p"></div>

      <v-btn
        flat
        color="rgb(184, 184, 184)"
        :icon="lockRatio ? 'mdi-lock' : 'mdi-lock-open-variant'"
        variant="plain"
        size="30px"
        @click="onLockClick"
      ></v-btn>

      <div class="lock-p" style="transform: scaleY(-1)"></div>
    </div>

    <div>
      <v-text-field
        v-model="dimensions.width"
        variant="outlined"
        label="Width"
        min="1"
        max-width="100"
        density="compact"
        type="number"
        hide-details
        class="mb-4"
        @update:modelValue="onWidthChange"
      />
      <v-text-field
        v-model="dimensions.height"
        variant="outlined"
        label="Height"
        min="1"
        max-width="100"
        density="compact"
        type="number"
        hide-details
        @update:modelValue="onHeightChange"
      />
    </div>
  </div>
</template>

<script>
export default {
  props: ["modelValue", "originalDimensions"],
  emits: ["update:modelValue"],

  data() {
    return { lockRatio: true };
  },

  watch: {
    originalDimensions(val) {
      this.dimensions.height = val.height;
      this.dimensions.width = val.width;
    },
  },

  computed: {
    dimensions: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit("update:modelValue", value);
      },
    },
    ratio() {
      return this.originalDimensions.width / this.originalDimensions.height;
    },
  },

  methods: {
    onHeightChange(value) {
      if (this.lockRatio) {
        this.dimensions.width = Math.round(value * this.ratio);
      }
    },
    onWidthChange(value) {
      if (this.lockRatio) {
        this.dimensions.height = Math.round(value / this.ratio);
      }
    },
    onLockClick() {
      this.lockRatio = !this.lockRatio;

      if (this.lockRatio) {
        this.dimensions.height = Math.round(this.dimensions.width / this.ratio);
      }
    },
  },
};
</script>

<style lang="css">
.lock-p {
  border-color: rgb(108, 108, 108);
  border-width: 1px 0 0px 1px;
  border-style: solid;
  border-radius: 3px 0 0 0;
  margin: 0 0 0 10px;
  width: 11px;
  align-items: center;
  flex-grow: 1;
}
</style>
