const ui = {
    setDefaultInputs: function() {
        document.querySelectorAll('input.temperatureOpe[type="number"]').forEach(input => {
            input.step = "0.01";
            input.value = "0";
        });
        document.querySelectorAll('input.pressureOpe[type="number"]').forEach(input => {
            input.min = "0";
            input.step = "0.01";
            input.value = "0";
        });
        document.querySelectorAll('input.gas-input[type="number"]').forEach(input => {
            input.min = "0";
            input.max = "100";
            input.step = "0.01";
            input.value = "0";
        });
    },
    showError: function(message) {
        alert(message);
    },
    showResults: function(data) {
        console.log("informacion: ",data);
        /*document.getElementById("Zf").innerText = data.z_detail;
        document.getElementById("rho_gerg").innerText = data.rho_gerg;
        document.getElementById("rho_detail").innerText = data.rho_detail;
        document.getElementById("z_gerg").innerText = data.z_gerg;
        document.getElementById("z_detail").innerText = data.z_detail;
        document.getElementById("results").style.display = "block";
        document.getElementById("error-message").style.display = "none";*/
    },
    showServerError: function(error) {
        document.getElementById("error-message").innerText = error;
        document.getElementById("error-message").style.display = "block";
        document.getElementById("results").style.display = "none";
    }
};