function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function setupLanguageSwitcher(url) {
    const switcher = document.getElementById('languageSwitcher');
    if (!switcher) return;

    switcher.addEventListener('change', function () {
        const selectedLang = this.value;

        fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({ language: selectedLang })
        })
        .then(response => {
            if (response.ok) {
                // Optional success message
                showAlert("Language switched successfully", "success");
                setTimeout(() => location.reload(), 500);
            } else {
                showAlert("Failed to change language", "danger");
            }
        })
        .catch(error => console.error("Language switch error:", error));
    });
}
