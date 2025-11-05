function showAlert(message, type = "info") {
    const container = document.createElement("div");
    container.className = `alert alert-${type} position-fixed top-0 end-0 m-3 shadow`;
    container.style.zIndex = 2000;
    container.innerText = message;
    document.body.appendChild(container);
    setTimeout(() => container.remove(), 3000);
}
