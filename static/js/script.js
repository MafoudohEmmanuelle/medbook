let currentLang = 'fr';

function applyTranslation(lang) {
    const elements = document.querySelectorAll('[data-translate]');
    elements.forEach(el => {
        const key = el.getAttribute('data-translate');
        if (translations[lang] && translations[lang][key]) {
            el.textContent = translations[lang][key];
        }
    });
    document.documentElement.setAttribute('data-lang', lang);
    currentLang = lang;
}

function toggleLanguage() {
    const newLang = currentLang === 'fr' ? 'en' : 'fr';
    applyTranslation(newLang);
    document.getElementById('langBtn').textContent = newLang.toUpperCase();
}

function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    localStorage.setItem('dark-theme', document.body.classList.contains('dark-theme'));
}

function loadTheme() {
    if (localStorage.getItem('dark-theme') === 'true') {
        document.body.classList.add('dark-theme');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadTheme();
    applyTranslation(currentLang);

    document.getElementById('themeBtn')?.addEventListener('click', toggleTheme);
    document.getElementById('langBtn')?.addEventListener('click', toggleLanguage);
});
