<template>
  <v-radio-group
    inline
    :value="modelValue"
    @input="$emit('update:modelValue', $event.target.value)"
  >
    <v-radio
      v-for="[direction, val] of directions"
      :label="direction"
      :value="val"
      :key="direction"
    />
  </v-radio-group>
</template>

<script>
export default {
  props: ["modelValue"],
  emits: ["update:modelValue"],
  data() {
    return {
      directions: [
        ["North", "n"],
        ["South", "s"],
        ["East", "e"],
        ["West", "w"],
      ],
    };
  },
};
</script>

<style scoped>
.radio-group {
  display: flex;
  gap: 16px;
}
.radio-option {
  display: flex;
  align-items: center;
}
</style>
