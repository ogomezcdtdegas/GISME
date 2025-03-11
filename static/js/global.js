document.addEventListener("DOMContentLoaded", function () {
    console.log("Script global cargado correctamente.");

    // Definir la función en el objeto window para que sea accesible en todos los scripts
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

    console.log("CSRF Token function registrada.");
});
