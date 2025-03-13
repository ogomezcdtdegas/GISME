import { getCSRFToken } from "./api.js";
import { registerEvents } from "./events.js";

document.addEventListener("DOMContentLoaded", function () {
    console.log("🔄 Script global cargado correctamente.");
    console.log("✅ CSRF Token:", getCSRFToken());

    // Registrar eventos
    registerEvents();
});