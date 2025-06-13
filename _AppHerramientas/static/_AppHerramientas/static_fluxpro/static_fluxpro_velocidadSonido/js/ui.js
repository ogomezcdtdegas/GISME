const ui = {
    setDefaultInputs: function() {
        document.querySelectorAll('input.temperatureOpe[type="number"]').forEach(input => {
            input.step = "0.0001";
            input.value = "0";
        });
        document.querySelectorAll('input.pressureOpe[type="number"]').forEach(input => {
            input.min = "0";
            input.step = "0.0001";
            input.value = "0";
        });
        document.querySelectorAll('input.temperatureBas[type="number"]').forEach(input => {
            input.step = "0.0001";
            input.value = "0";
        });
        document.querySelectorAll('input.pressureBas[type="number"]').forEach(input => {
            input.min = "0";
            input.step = "0.0001";
            input.value = "0";
        });
        document.querySelectorAll('input.gas-input[type="number"]').forEach(input => {
            input.min = "0";
            input.max = "100";
            input.step = "0.0001";
            input.value = "0";
        });
    },
    showError: function(message) {
        alert(message);
    },
    showResults: function(data) {
        console.log("informacion: ",data);
    },
    showServerError: function(error) {
        document.getElementById("error-message").innerText = error;
        document.getElementById("error-message").style.display = "block";
        document.getElementById("results").style.display = "none";
    }
};