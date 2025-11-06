const App = {
    // --- Utilities ---
    utils: {
        showAlert(message, type = "info") {
            const container = document.createElement("div");
            container.className = `alert alert-${type} position-fixed top-0 end-0 m-3 shadow`;
            container.style.zIndex = 2000;
            container.innerText = message;
            document.body.appendChild(container);
            setTimeout(() => container.remove(), 3000);
        },

        getCookie(name) {
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
    },

    // --- Theme (Dark/Light) ---
    theme: {
        init() {
            if (localStorage.getItem("dark-theme") === "true") {
                document.body.classList.add("dark-theme");
            }

            const themeBtn = document.getElementById("themeBtn");
            if (themeBtn) {
                themeBtn.addEventListener("click", () => {
                    document.body.classList.toggle("dark-theme");
                    localStorage.setItem(
                        "dark-theme",
                        document.body.classList.contains("dark-theme")
                    );
                });
            }
        }
    },

    // --- Language Switcher ---
    language: {
        init(url) {
            const switcher = document.getElementById('languageSwitcher');
            if (!switcher) return;

            switcher.addEventListener('change', function () {
                const selectedLang = this.value;

                fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": App.utils.getCookie("csrftoken")
                    },
                    body: JSON.stringify({ language: selectedLang })
                })
                .then(response => {
                    if (response.ok) {
                        App.utils.showAlert("Language switched successfully", "success");
                        setTimeout(() => location.reload(), 500);
                    } else {
                        App.utils.showAlert("Failed to change language", "danger");
                    }
                })
                .catch(error => console.error("Language switch error:", error));
            });
        }
    },

    // --- Logout Confirmation ---
    logout: {
        init() {
            const logoutBtn = document.querySelector(".logout, .logout-btn");
            if (logoutBtn) {
                logoutBtn.addEventListener("click", (e) => {
                    e.preventDefault();
                    if (confirm("Are you sure you want to log out?")) {
                        window.location.href = logoutBtn.getAttribute("href");
                    }
                });
            }
        }
    },

    // --- Table Search Filter ---
    searchFilter: {
        init() {
            const searchInputs = document.querySelectorAll(".search-bar input");
            searchInputs.forEach(input => {
                input.addEventListener("input", (e) => {
                    const term = e.target.value.toLowerCase();
                    const table = e.target.closest("section").querySelector("tbody");
                    if (!table) return;
                    Array.from(table.rows).forEach(row => {
                        const text = row.textContent.toLowerCase();
                        row.style.display = text.includes(term) ? "" : "none";
                    });
                });
            });
        }
    },

    // --- Initialize all modules ---
    init() {
        this.theme.init();
        this.language.init("/accounts/switch-language/"); // update URL if needed
        this.logout.init();
        this.searchFilter.init();
    }
};

// Initialize App on DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {
    App.init();
});
