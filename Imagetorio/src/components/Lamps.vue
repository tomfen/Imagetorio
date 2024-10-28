<template>
  <v-container>
    <v-row>
      <v-col>
        <v-img :src="imageUrl" max-height="500px" />
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
        <SizeSelect />
      </v-col>
    </v-row>
    <BlueprintBox @generate="generate"></BlueprintBox>
  </v-container>
</template>

<script>
import BlueprintBox from "./BlueprintBox.vue";
import SizeSelect from "./SizeSelect.vue";

export default {
  data() {
    return {
      imageUrl: "",
    };
  },
  methods: {
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
    generate() {
      if (!this.imageUrl) return;
      console.log("a");
    },
  },
  components: { SizeSelect },
};
</script>
