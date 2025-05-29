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
                document.getElementById("w").value = data.Velocidad_sonido;
                document.getElementById("desv").value = data.Desviación;
            }
        });
    }
};