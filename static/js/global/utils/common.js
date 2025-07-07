// notifications.js - Utilidades para notificaciones y mensajes
export const Notifications = {
    showSuccess(message) {
        alert("✅ " + message); // Aquí podrías usar una librería de toasts
    },

    showError(message) {
        alert("❌ " + message);
    },

    showWarning(message) {
        alert("⚠️ " + message);
    }
};

// Utilidades de formularios
export const FormUtils = {
    resetForm(formId) {
        document.getElementById(formId)?.reset();
    },

    getFormData(formId) {
        const form = document.getElementById(formId);
        if (!form) return null;
        return new FormData(form);
    },

    getInputValue(inputId) {
        return document.getElementById(inputId)?.value;
    }
};
