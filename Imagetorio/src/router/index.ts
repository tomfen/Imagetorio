// Composables
import Decode from "@/components/Decode.vue";
import Lamps from "@/components/Lamps.vue";
import Printer from "@/components/Printer.vue";
import { createRouter, createWebHashHistory } from "vue-router/auto";

const routes = [
  {
    path: "/",
    name: "index",
    redirect: "printer",
    children: [
      {
        path: "printer",
        name: "printer",
        component: Printer,
      },
      {
        path: "lamps",
        name: "lamps",
        component: Lamps,
      },
      {
        path: "decode",
        name: "decode",
        component: Decode,
      },
    ],
  },
];

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes,
});

// Workaround for https://github.com/vitejs/vite/issues/11804
router.onError((err, to) => {
  if (err?.message?.includes?.("Failed to fetch dynamically imported module")) {
    if (!localStorage.getItem("vuetify:dynamic-reload")) {
      console.log("Reloading page to fix dynamic import error");
      localStorage.setItem("vuetify:dynamic-reload", "true");
      location.assign(to.fullPath);
    } else {
      console.error("Dynamic import error, reloading page did not fix it", err);
    }
  } else {
    console.error(err);
  }
});

router.isReady().then(() => {
  localStorage.removeItem("vuetify:dynamic-reload");
});

export default router;
