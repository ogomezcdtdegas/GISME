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
                console.log("dataCalc: ", data);
                document.getElementById("Zf").value = data.z_gerg;
                document.getElementById("Zb").value = data.z_gergBas;
                document.getElementById("μ").value = data.mu;
                document.getElementById("mm").value = data.mm;
                document.getElementById("ρ").value = data.rho_detail;
                document.getElementById("Hv").value = data.HHV_BTU_ft3_real;
                document.getElementById("dx").value = data.d;
                document.getElementById("gr").value = data.rho_detailRelative;
                document.getElementById("lw").value = data.indice_Wobbe;
            }
        });
    }
};