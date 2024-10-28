<template>
  <div>
    <v-text-field
      v-model="height"
      variant="outlined"
      label="Max height"
      min="1"
      max="1000"
      max-width="100"
      density="compact"
      type="number"
    />
    <v-text-field
      v-model="width"
      variant="outlined"
      label="Max width"
      min="1"
      max="1000"
      max-width="100"
      density="compact"
      type="number"
    />
  </div>
</template>

<script>
export default {
  data() {
    return {
      height: 100,
      width: 200,
    };
  },
};
</script>
