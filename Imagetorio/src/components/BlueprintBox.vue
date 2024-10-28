<template>
  <div class="blueprintBox">
    <textarea readonly class="blueprint" id="blueprint" spellcheck="false">{{
      content
    }}</textarea>
    <div>
      <button round flat @click="$emit('generate')">
        <v-icon>mdi-refresh</v-icon>
      </button>

      <button round flat @click="$emit('copy')">
        <v-icon>mdi-clipboard-outline</v-icon>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: ["content"],
  emits: ["generate", "copy"],
};
</script>

<style lang="css">
.blueprintBox {
  border: 2px solid rgb(235, 235, 235);
  background-image: url("@/assets/blueprint.svg"),
    linear-gradient(30deg, rgb(77, 99, 146) 0%, rgb(64, 78, 124) 100%);
  color: white;
  margin: 5px;
  padding: 3px;
  float: left;
}

.blueprint {
  font-family: consolas;
  padding: 0px;
  overflow: hidden;
  background: transparent;
  height: 100px;
  margin: 0px;
  border: dashed 1px rgba(255, 255, 255, 0.6);
  color: white;
  vertical-align: top;
}
</style>
