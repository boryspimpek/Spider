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
    const walkForwardBtn = document.getElementById('walk forward');
    if (walkForwardBtn) {
        walkForwardBtn.addEventListener('mousedown', () => sendRequest('/walkforward'));
        walkForwardBtn.addEventListener('mouseup', () => sendRequest('/stopwalk'));
        walkForwardBtn.addEventListener('touchstart', (e) => {e.preventDefault(); sendRequest('/walkforward');});
        walkForwardBtn.addEventListener('touchend', (e) => {e.preventDefault();sendRequest('/stopwalk');});
    }

    // Obsługa przycisku walk back (touch/hold)
    const walkBackBtn = document.getElementById('walk back');
    if (walkBackBtn) {
        walkBackBtn.addEventListener('mousedown', () => sendRequest('/walkback'));
        walkBackBtn.addEventListener('mouseup', () => sendRequest('/stopwalk'));
        walkBackBtn.addEventListener('touchstart', (e) => {e.preventDefault(); sendRequest('/walkback');});
        walkBackBtn.addEventListener('touchend', (e) => {e.preventDefault();sendRequest('/stopwalk');});
    }

    // Obsługa przycisku turn right (touch/hold)
    const turnRightBtn = document.getElementById('turn right');
    if (turnRightBtn) {
        turnRightBtn.addEventListener('mousedown', () => sendRequest('/turnright'));
        turnRightBtn.addEventListener('mouseup', () => sendRequest('/stopwalk'));
        turnRightBtn.addEventListener('touchstart', (e) => {e.preventDefault(); sendRequest('/turnright');});
        turnRightBtn.addEventListener('touchend', (e) => {e.preventDefault();sendRequest('/stopwalk');});
    }

    // Obsługa przycisku turn left (touch/hold)
    const turnLeftBtn = document.getElementById('turn left');
    if (turnLeftBtn) {
        turnLeftBtn.addEventListener('mousedown', () => sendRequest('/turnleft'));
        turnLeftBtn.addEventListener('mouseup', () => sendRequest('/stopwalk'));
        turnLeftBtn.addEventListener('touchstart', (e) => {e.preventDefault(); sendRequest('/turnleft');});
        turnLeftBtn.addEventListener('touchend', (e) => {e.preventDefault();sendRequest('/stopwalk');});
    }


    // Udostępnij funkcję sendCommand globalnie dla innych przycisków
    window.sendCommand = sendCommand;
});