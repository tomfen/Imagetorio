<template>
  <v-container>
    <v-row>
      <v-btn @click="selectAll">select all</v-btn>
      <v-btn @click="clear">clear</v-btn>
    </v-row>
    <v-row>
      <v-checkbox
        density="compact"
        width="300px"
        class="mr-3"
        hide-details
        :key="name"
        :value="name"
        :label="readableName(name)"
        v-model="selected"
        v-for="([r, g, b], name) in colors"
      >
        <template #prepend>
          <v-icon :color="`rgb(${r}, ${g}, ${b})`" class="mr-n5"
            >mdi-square-rounded</v-icon
          >
        </template>
        <template #append>
          {{ itemCount[name] }}
        </template>
      </v-checkbox>
    </v-row>
  </v-container>
</template>

<script>
export default {
  props: ["modelValue", "itemCount"],
  emits: ["update:modelValue", "update:palette"],
  computed: {
    selected: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit("update:modelValue", value);
        this.$emit(
          "update:palette",
          value.map((key) => this.colors[key])
        );
      },
    },
  },
  methods: {
    clear() {
      this.selected = [];
    },
    selectAll() {
      this.selected = Object.keys(this.colors);
    },
  },
  data() {
    return {
      colors: {
        "advanced-circuit": [159, 83, 53],
        "artillery-shell": [117, 87, 70],
        "artillery-turret": [90, 84, 72],
        "assembling-machine-2": [92, 98, 103],
        "assembling-machine-3": [112, 111, 89],
        "atomic-bomb": [68, 114, 62],
        "automation-science-pack": [136, 90, 98],
        battery: [99, 103, 106],
        "battery-equipment": [59, 173, 54],
        beacon: [105, 95, 88],
        "belt-immunity-equipment": [203, 107, 89],
        "burner-inserter": [81, 71, 64],
        "cannon-shell": [75, 62, 52],
        "chemical-plant": [103, 83, 63],
        "chemical-science-pack": [90, 138, 154],
        "cliff-explosives": [56, 81, 98],
        "cluster-grenade": [73, 56, 51],
        coal: [21, 21, 21],
        "combat-shotgun": [104, 81, 72],
        concrete: [115, 114, 113],
        "constant-combinator": [89, 58, 52],
        "copper-cable": [133, 94, 76],
        "copper-ore": [113, 66, 46],
        "copper-plate": [141, 82, 67],
        "crude-oil-barrel": [84, 83, 78],
        "discharge-defense-equipment": [117, 116, 115],
        "discharge-defense-remote": [89, 89, 130],
        "effectivity-module": [70, 129, 52],
        "electric-engine-unit": [119, 78, 75],
        "electronic-circuit": [109, 138, 54],
        "empty-barrel": [99, 103, 95],
        "engine-unit": [121, 101, 77],
        "explosive-cannon-shell": [83, 55, 49],
        "explosive-rocket": [90, 72, 68],
        "explosive-uranium-cannon-shell": [69, 85, 47],
        explosives: [109, 59, 50],
        "express-transport-belt": [104, 102, 107],
        "express-underground-belt": [74, 93, 105],
        "fast-inserter": [75, 79, 82],
        "fast-transport-belt": [120, 103, 100],
        "fast-underground-belt": [102, 64, 63],
        "filter-inserter": [80, 62, 81],
        "firearm-magazine": [76, 70, 43],
        flamethrower: [75, 66, 63],
        "flamethrower-turret": [87, 69, 56],
        gate: [59, 50, 44],
        "green-wire": [66, 127, 56],
        grenade: [62, 63, 59],
        "gun-turret": [98, 90, 82],
        "heat-pipe": [143, 74, 56],
        "heavy-armor": [83, 68, 51],
        "heavy-oil-barrel": [113, 91, 68],
        inserter: [112, 83, 58],
        "iron-chest": [104, 95, 87],
        "iron-gear-wheel": [91, 88, 83],
        "iron-ore": [56, 74, 86],
        "iron-plate": [99, 98, 100],
        "iron-stick": [93, 85, 84],
        lab: [106, 108, 113],
        "land-mine": [91, 77, 62],
        landfill: [85, 84, 35],
        "laser-turret": [89, 76, 61],
        "light-armor": [83, 69, 59],
        "light-oil-barrel": [121, 103, 56],
        "logistic-chest-active-provider": [90, 72, 100],
        "logistic-chest-buffer": [74, 112, 74],
        "logistic-chest-passive-provider": [120, 73, 63],
        "logistic-chest-requester": [77, 98, 105],
        "logistic-chest-storage": [110, 95, 59],
        "logistic-science-pack": [104, 129, 102],
        "long-handed-inserter": [105, 60, 54],
        "low-density-structure": [86, 71, 55],
        "lubricant-barrel": [82, 103, 69],
        "military-science-pack": [110, 112, 117],
        "modular-armor": [103, 73, 46],
        "nuclear-fuel": [69, 122, 62],
        "oil-refinery": [84, 60, 42],
        "petroleum-gas-barrel": [107, 106, 102],
        "piercing-rounds-magazine": [73, 43, 43],
        "piercing-shotgun-shell": [89, 77, 68],
        pipe: [96, 90, 76],
        pistol: [75, 71, 67],
        "plastic-bar": [153, 150, 150],
        "poison-capsule": [83, 150, 56],
        "power-armor": [91, 61, 35],
        "power-armor-mk2": [108, 73, 41],
        "power-switch": [79, 71, 66],
        "processing-unit": [113, 100, 168],
        "production-science-pack": [127, 110, 147],
        "productivity-module": [157, 111, 59],
        pumpjack: [66, 72, 35],
        radar: [98, 93, 78],
        rail: [97, 89, 82],
        "rail-chain-signal": [73, 86, 99],
        "red-wire": [150, 40, 40],
        rocket: [94, 82, 69],
        "rocket-fuel": [96, 82, 72],
        "rocket-launcher": [81, 78, 71],
        "rocket-silo": [93, 81, 70],
        "shotgun-shell": [120, 62, 39],
        "slowdown-capsule": [88, 135, 183],
        "small-lamp": [180, 180, 180],
        "solar-panel": [83, 91, 92],
        "solar-panel-equipment": [99, 102, 122],
        "solid-fuel": [63, 60, 60],
        "space-science-pack": [151, 151, 154],
        "speed-module": [59, 130, 153],
        "stack-filter-inserter": [105, 100, 96],
        "stack-inserter": [92, 91, 53],
        "steel-chest": [115, 110, 117],
        "steel-plate": [132, 132, 122],
        stone: [80, 71, 57],
        "stone-brick": [102, 102, 98],
        "stone-furnace": [102, 87, 57],
        "stone-wall": [91, 86, 77],
        "storage-tank": [94, 87, 78],
        "submachine-gun": [69, 64, 61],
        sulfur: [153, 139, 74],
        "sulfuric-acid-barrel": [109, 128, 59],
        "transport-belt": [120, 112, 97],
        "underground-belt": [104, 90, 66],
        "uranium-235": [61, 166, 43],
        "uranium-238": [41, 76, 41],
        "uranium-cannon-shell": [60, 99, 47],
        "uranium-fuel-cell": [62, 134, 64],
        "uranium-ore": [74, 116, 32],
        "uranium-rounds-magazine": [31, 113, 40],
        "utility-science-pack": [149, 135, 114],
        "water-barrel": [96, 103, 101],
        wood: [114, 72, 51],
        "wooden-chest": [118, 92, 56],
        "blueprint-book": [65, 106, 134],
        blueprint: [37, 115, 163],
        "deconstruction-planner": [169, 55, 57],
        "raw-fish": [134, 100, 75],
        "upgrade-planner": [130, 148, 2],
      },

      readableName: (name) => {
        let readable = name
          .replace("underground", "under.")
          .replace("science-pack", "science")
          .replace("cannon-shell", "shell")
          .replace("logistic-chest", "logistic")
          .replace("defense", "")
          .replace(/-/g, " ");

        return readable[0].toUpperCase() + readable.substr(1);
      },
    };
  },
  mounted() {
    this.selectAll();
  },
};
</script>
