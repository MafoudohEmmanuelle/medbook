document.addEventListener("DOMContentLoaded", () => {
    // Load dark/light theme from localStorage
    if (localStorage.getItem("dark-theme") === "true") {
        document.body.classList.add("dark-theme");
    }

    // Initialize language switcher
    if (typeof setupLanguageSwitcher === "function") {
        setupLanguageSwitcher("/accounts/switch-language/"); // make sure URL matches your Django url
    }

    const logoutBtn = document.querySelector(".logout, .logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", (e) => {
            e.preventDefault();
            if (confirm("Are you sure you want to log out?")) {
                window.location.href = logoutBtn.getAttribute("href");
            }
        });
    }

    // Theme toggle button 
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
});
