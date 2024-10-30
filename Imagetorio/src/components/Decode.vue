<template>
  <v-textarea @update:modelValue="decode"></v-textarea>
  <div style="position: absolute; width: 100%">
    <v-btn
      icon="mdi-clipboard-outline"
      large
      style="position: absolute; right: 40px; top: 15px; z-index: 999"
      @click="copyToClipboard"
    ></v-btn>
  </div>
  <v-textarea
    density="comfortable"
    :value="decoded"
    readonly
    rows="50"
    variant="outlined"
  >
  </v-textarea>
  <v-snackbar v-model="snackbar" timeout="2000">Copied to clipboard</v-snackbar>
</template>

<script setup>
import pako from "pako";
import { ref } from "vue";
import { reactive } from "vue";

const decoded = ref("");
const snackbar = ref(false);

function decode(blueprint) {
  try {
    let base64 = blueprint.trim().substring(1);
    let binary = atob(base64);
    let json = pako.inflate(binary, { to: "string" });

    decoded.value = JSON.stringify(JSON.parse(json), null, 4);
  } catch (error) {}
}

function copyToClipboard() {
  navigator.clipboard.writeText(decoded.value);
  snackbar.value = true;
}
</script>
