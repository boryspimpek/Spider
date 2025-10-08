// script.js
document.addEventListener('DOMContentLoaded', () => {
    function sendRequest(url) {
        fetch(url)
            .then(response => response.json())
            .then(data => {
                document.getElementById('status').textContent = data.status || 'Command sent';
            })
            .catch(err => {
                console.error('Request failed:', err);
                document.getElementById('status').textContent = 'Error sending command';
            });
    }

    function sendCommand(command) {
        fetch('/' + command)
            .then(response => response.json())
            .then(data => {
                document.getElementById('status').textContent = data.status || 'Command sent';
            })
            .catch(err => {
                console.error('Request failed:', err);
                document.getElementById('status').textContent = 'Error sending command';
            });
    }

    // Obsługa przycisku walk forward (touch/hold)
    const walkBtn = document.getElementById('walk forward');
    if (walkBtn) {
        walkBtn.addEventListener('mousedown', () => sendRequest('/walkforward/start'));
        walkBtn.addEventListener('mouseup', () => sendRequest('/stopwalk'));
        walkBtn.addEventListener('touchstart', (e) => {
            e.preventDefault();
            sendRequest('/walkforward/start');
        });
        walkBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            sendRequest('/stopwalk');
        });
    }

    // Udostępnij funkcję sendCommand globalnie dla innych przycisków
    window.sendCommand = sendCommand;
});