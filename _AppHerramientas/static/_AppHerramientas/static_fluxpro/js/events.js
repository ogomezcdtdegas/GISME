const events = {
    attachFormEvents: function() {
        document.getElementById("condicionesForm").addEventListener("submit", function(event) {
            // Validaciones
            if (!events.validatePressure()) { event.preventDefault(); return; }
            if (!events.validateTemperature()) { event.preventDefault(); return; }
            if (!events.validateInputs()) { event.preventDefault(); return; }
            if (!events.validateAtLeastOneComponent()) { event.preventDefault(); return; }

            event.preventDefault();

            // Preparar datos y llamar a la API
            let formData = new FormData(this);
            let jsonData = {};
            formData.forEach((value, key) => { jsonData[key] = value; });

            api.sendForm(jsonData);
        });
    },
    validatePressure: function() {
        const pressureInput = document.getElementById("pressure");
        if (pressureInput && (parseFloat(pressureInput.value) <= 0 || isNaN(parseFloat(pressureInput.value)))) {
            ui.showError("La presión de operación debe ser ingresada de 0 en adelante.");
            pressureInput.focus();
            return false;
        }
        return true;
    },
    validateTemperature: function() {
        const temperatureInput = document.getElementById("temperature");
        if (temperatureInput && (isNaN(parseFloat(temperatureInput.value)))) {
            ui.showError("La temperatura de operación debe ser ingresada.");
            temperatureInput.focus();
            return false;
        }
        return true;
    },
    validateInputs: function() {
        let vacio = false;
        document.querySelectorAll('input.gas-input[type="number"]').forEach(function(input) {
            if (input.value === "" || input.value === null) {
                vacio = true;
                input.focus();
            }
        });
        if (vacio) {
            ui.showError("Todos los campos de composición deben tener un valor (puede ser 0).");
            return false;
        }
        return true;
    },
    validateAtLeastOneComponent: function() {
        let algunNoCero = false;
        document.querySelectorAll('input.gas-input[type="number"]').forEach(function(input) {
            if (parseFloat(input.value) !== 0 && input.value !== "") {
                algunNoCero = true;
            }
        });
        if (!algunNoCero) {
            ui.showError("Debe haber al menos un componente de la composición diferente de 0%");
            return false;
        }
        return true;
    }
};