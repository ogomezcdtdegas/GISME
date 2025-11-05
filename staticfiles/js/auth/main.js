document.getElementById("login-form").addEventListener("submit", async function(event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const errorMessage = document.getElementById("error-message");

    try {
        const response = await fetch("/api/token/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem("access_token", data.access);
            localStorage.setItem("refresh_token", data.refresh);
            window.location.href = "/";  // Redirige al home
        } else {
            errorMessage.textContent = data.detail || "Credenciales incorrectas";
            errorMessage.classList.remove("d-none");
        }
    } catch (error) {
        console.error("Error al iniciar sesión:", error);
        errorMessage.textContent = "Error en la conexión con el servidor";
        errorMessage.classList.remove("d-none");
    }
});
