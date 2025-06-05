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
                document.getElementById("vb").value = data.volBase;
                document.getElementById("desv").value = data.Desviación;
                document.getElementById("zf").value = data.zf;
                document.getElementById("zb").value = data.zb;
            }
        });
    }
};