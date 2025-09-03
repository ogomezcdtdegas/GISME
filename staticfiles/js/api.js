console.log("📡 api.js cargado.");

// Función para obtener el CSRF Token
window.getCSRFToken = function () {
    let csrfToken = null;
    document.cookie.split(";").forEach(cookie => {
        let [name, value] = cookie.trim().split("=");
        if (name === "csrftoken") {
            csrfToken = value;
        }
    });
    return csrfToken;
};
console.log("✅ CSRF Token function registrada.");
