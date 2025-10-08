// Uniwersalna funkcja do wysyłania komend do robota
function sendCommand(action) {
    const statusDiv = document.getElementById('status');
    
    // Wyświetl informację o wysyłaniu
    updateStatus(`Wysyłam komendę: ${action}...`, 'info');
    
    fetch(`/move/${action}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateStatus(`✓ ${data.message}`, 'success');
        } else {
            updateStatus(`✗ ${data.message}`, 'error');
        }
    })
    .catch(error => {
        updateStatus(`✗ Błąd połączenia: ${error.message}`, 'error');
        console.error('Error:', error);
    });
}

// Funkcja do aktualizacji statusu
function updateStatus(message, type) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type}`;
    
    // Automatycznie wyczyść status po 5 sekundach
    setTimeout(() => {
        if (statusDiv.textContent === message) {
            statusDiv.textContent = '';
            statusDiv.className = 'status-message';
        }
    }, 5000);
}

// Obsługa gestów mobilnych (opcjonalne)
document.addEventListener('DOMContentLoaded', function() {
    // Zapobiegnij podwójnemu tapnięciu na mobilnych
    let lastTap = 0;
    document.addEventListener('touchend', function (e) {
        const currentTime = new Date().getTime();
        const tapLength = currentTime - lastTap;
        if (tapLength < 500 && tapLength > 0) {
            e.preventDefault();
        }
        lastTap = currentTime;
    });
    
    // Pokaż wiadomość powitalną
    updateStatus('Robot gotowy do sterowania', 'success');
});