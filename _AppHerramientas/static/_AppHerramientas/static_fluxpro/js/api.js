const api = {
    sendForm: function(jsonData) {
        fetch(window.apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": window.csrfToken
            },
            body: JSON.stringify(jsonData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                ui.showServerError(data.error);
            } else {
                ui.showResults(data);
                document.getElementById("Zf").value = data.z_gerg;
                document.getElementById("μ").value = data.mu;
                document.getElementById("mm").value = data.mm;
                document.getElementById("ρ").value = data.rho_gerg;
                document.getElementById("dx").value = data.d;
            }
        });
    }
};