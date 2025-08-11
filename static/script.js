// Uniwersalna funkcja do wysyłania komend do robota
function sendCommand(action) {
    const button = event.target;
    const statusDiv = document.getElementById('status');
    
    // Dodaj efekt wysyłania
    button.classList.add('sending');
    
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
    })
    .finally(() => {
        // Usuń efekt wysyłania po 500ms
        setTimeout(() => {
            button.classList.remove('sending');
        }, 500);
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
    
    // Dodaj efekt dotknięcia dla przycisków na urządzeniach mobilnych
    const buttons = document.querySelectorAll('.robot-btn:not(.empty-slot)');
    buttons.forEach(button => {
        button.addEventListener('touchstart', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 0 20px #00ff41';
        });
        
        button.addEventListener('touchend', function() {
            setTimeout(() => {
                if (!this.classList.contains('sending')) {
                    this.style.transform = '';
                    this.style.boxShadow = '';
                }
            }, 100);
        });
    });
    
    // Pokaż wiadomość powitalną
    updateStatus('Robot gotowy do sterowania', 'success');
});