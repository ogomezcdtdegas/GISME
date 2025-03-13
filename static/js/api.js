// Obtener el CSRF Token desde las cookies
export function getCSRFToken() {
    let csrfToken = null;
    document.cookie.split(";").forEach(cookie => {
        let [name, value] = cookie.trim().split("=");
        if (name === "csrftoken") {
            csrfToken = value;
        }
    });
    return csrfToken;
}
