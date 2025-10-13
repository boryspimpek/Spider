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
        walkForwardBtn.addEventListener('mousedown', () => sendRequest('/move/forward'));
        walkForwardBtn.addEventListener('mouseup', () => sendRequest('/stop'));
        walkForwardBtn.addEventListener('touchstart', (e) => {e.preventDefault(); sendRequest('//move/forward');});
        walkForwardBtn.addEventListener('touchend', (e) => {e.preventDefault();sendRequest('/stop');});
    }

    // Obsługa przycisku walk backward
    const walkBackwardBtn = document.getElementById('walk backward');
    if (walkBackwardBtn) {
        walkBackwardBtn.addEventListener('mousedown', () => sendRequest('/move/backward'));
        walkBackwardBtn.addEventListener('mouseup', () => sendRequest('/stop'));
        walkBackwardBtn.addEventListener('touchstart', (e) => {e.preventDefault(); sendRequest('/move/backward');});
        walkBackwardBtn.addEventListener('touchend', (e) => {e.preventDefault(); sendRequest('/stop');});
    }

    // Obsługa przycisku turn left
    const turnLeftBtn = document.getElementById('turn left');
    if (turnLeftBtn) {
        turnLeftBtn.addEventListener('mousedown', () => sendRequest('/move/left'));
        turnLeftBtn.addEventListener('mouseup', () => sendRequest('/stop'));
        turnLeftBtn.addEventListener('touchstart', (e) => {e.preventDefault(); sendRequest('/move/left');});
        turnLeftBtn.addEventListener('touchend', (e) => {e.preventDefault(); sendRequest('/stop');});
    }

    // Obsługa przycisku turn right
    const turnRightBtn = document.getElementById('turn right');
    if (turnRightBtn) {
        turnRightBtn.addEventListener('mousedown', () => sendRequest('/move/right'));
        turnRightBtn.addEventListener('mouseup', () => sendRequest('/stop'));
        turnRightBtn.addEventListener('touchstart', (e) => {e.preventDefault(); sendRequest('/move/right');});
        turnRightBtn.addEventListener('touchend', (e) => {e.preventDefault(); sendRequest('/stop');});
    }
    
    // Joystick Control
    (function() {
        const wrapper = document.getElementById('joystickWrapper');
        const handle = document.getElementById('joystickHandle');
        const displayX = document.getElementById('joystickX');
        const displayY = document.getElementById('joystickY');
        
        let isDragging = false;
        let centerX, centerY, maxDistance;
        let currentX = 0, currentY = 0;
        let sendInterval = null;
        
        function init() {
            const rect = wrapper.getBoundingClientRect();
            centerX = rect.width / 2;
            centerY = rect.height / 2;
            maxDistance = (rect.width / 2) - 30; // Odległość od środka minus promień handle
        }
        
        function updateHandlePosition(x, y) {
            handle.style.left = `${centerX + x}px`;
            handle.style.top = `${centerY + y}px`;
            handle.style.transform = 'translate(-50%, -50%)';
        }
        
        function normalizeCoordinates(x, y) {
            // Normalizuj do zakresu -1 do 1
            const normalizedX = Math.max(-1, Math.min(1, x / maxDistance));
            const normalizedY = Math.max(-1, Math.min(1, -y / maxDistance)); // Odwróć Y (góra = dodatnie)
            return { x: normalizedX, y: normalizedY };
        }
        
        function sendJoystickData(x, y) {
            fetch('/joystick', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ x, y })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Opcjonalnie: pokaż status
                    // console.log('Joystick OK:', data.message);
                }
            })
            .catch(error => {
                console.error('Joystick error:', error);
            });
        }
        
        function startDragging(e) {
            isDragging = true;
            handle.style.cursor = 'grabbing';
            init();
            
            // Wysyłaj dane co 100ms podczas przeciągania
            sendInterval = setInterval(() => {
                if (isDragging) {
                    const normalized = normalizeCoordinates(currentX, currentY);
                    sendJoystickData(normalized.x, normalized.y);
                }
            }, 100);
            
            e.preventDefault();
        }
        
        function stopDragging() {
            if (!isDragging) return;
            
            isDragging = false;
            handle.style.cursor = 'grab';
            
            // Wyczyść interval
            if (sendInterval) {
                clearInterval(sendInterval);
                sendInterval = null;
            }
            
            // Wróć do środka z animacją
            currentX = 0;
            currentY = 0;
            handle.style.transition = 'left 0.3s, top 0.3s';
            updateHandlePosition(0, 0);
            
            // Wyślij pozycję neutralną
            sendJoystickData(0, 0);
            
            // Zaktualizuj wyświetlanie
            displayX.textContent = '0.00';
            displayY.textContent = '0.00';
            
            setTimeout(() => {
                handle.style.transition = '';
            }, 300);
        }
        
        function onMove(clientX, clientY) {
            if (!isDragging) return;
            
            const rect = wrapper.getBoundingClientRect();
            let x = clientX - rect.left - centerX;
            let y = clientY - rect.top - centerY;
            
            // Ogranicz do okręgu
            const distance = Math.sqrt(x * x + y * y);
            if (distance > maxDistance) {
                const angle = Math.atan2(y, x);
                x = Math.cos(angle) * maxDistance;
                y = Math.sin(angle) * maxDistance;
            }
            
            currentX = x;
            currentY = y;
            
            updateHandlePosition(x, y);
            
            // Zaktualizuj wyświetlanie
            const normalized = normalizeCoordinates(x, y);
            displayX.textContent = normalized.x.toFixed(2);
            displayY.textContent = normalized.y.toFixed(2);
        }
        
        // Event listeners - mysz
        handle.addEventListener('mousedown', startDragging);
        document.addEventListener('mouseup', stopDragging);
        document.addEventListener('mousemove', (e) => {
            onMove(e.clientX, e.clientY);
        });
        
        // Event listeners - dotyk
        handle.addEventListener('touchstart', (e) => {
            startDragging(e);
        });
        document.addEventListener('touchend', stopDragging);
        document.addEventListener('touchmove', (e) => {
            if (isDragging && e.touches.length > 0) {
                onMove(e.touches[0].clientX, e.touches[0].clientY);
                e.preventDefault();
            }
        });
    })(); // Immediately invoke the joystick function

    // Slider Control (Vertical)
    (function() {
        const wrapper = document.getElementById('sliderWrapper');
        const handle = document.getElementById('sliderHandle');
        const displayValue = document.getElementById('sliderValue');
        const displayAngle = document.getElementById('sliderAngle');
        
        let isDragging = false;
        let centerY, maxDistance;
        let currentY = 0;
        let sendTimeout = null;
        let releaseTimeout = null;
        
        const MAX_ANGLE_CHANGE = 30; // Maksymalna zmiana kąta (+/- od 90°)
        
        function init() {
            const rect = wrapper.getBoundingClientRect();
            centerY = rect.height / 2;
            maxDistance = (rect.height / 2) - 35; // Odległość od środka minus margines
        }
        
        function updateHandlePosition(y) {
            handle.style.top = `${centerY + y}px`;
            handle.style.transform = 'translate(-50%, -50%)';
        }
        
        function normalizeValue(y) {
            // Normalizuj do zakresu -1 do 1
            // y dodatnie = dół (wartość ujemna), y ujemne = góra (wartość dodatnia)
            return Math.max(-1, Math.min(1, -y / maxDistance));
        }
        
        function valueToAngle(value) {
            // value: -1 do 1
            // -1 = 120°, 0 = 90°, 1 = 60°
            return Math.round(90 - (value * MAX_ANGLE_CHANGE));
        }
        
        let lastSendTime = 0;
        const SEND_INTERVAL = 100; // Wysyłaj co 100ms (tak jak joystick)
        
        function sendSliderData(value) {
            const now = Date.now();
            
            // Wysyłaj tylko jeśli minęło odpowiednio dużo czasu
            if (now - lastSendTime < SEND_INTERVAL) {
                return;
            }
            
            lastSendTime = now;
            
            fetch('/slider', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ value })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // console.log('Slider OK:', data.message);
                }
            })
            .catch(error => {
                console.error('Slider error:', error);
            });
        }
        
        function returnToCenter() {
            // Czekaj 500ms po puszczeniu przed powrotem
            releaseTimeout = setTimeout(() => {
                currentY = 0;
                handle.style.transition = 'top 0.4s ease-out';
                updateHandlePosition(0);
                
                // Wyślij pozycję neutralną
                sendSliderData(0);
                
                // Zaktualizuj wyświetlanie
                displayValue.textContent = '0.00';
                displayAngle.textContent = '90';
                
                setTimeout(() => {
                    handle.style.transition = '';
                }, 400);
            }, 500);
        }
        
        function startDragging(e) {
            isDragging = true;
            handle.style.cursor = 'grabbing';
            init();
            
            // Anuluj powrót do środka
            if (releaseTimeout) {
                clearTimeout(releaseTimeout);
                releaseTimeout = null;
            }
            
            e.preventDefault();
        }
        
        function stopDragging() {
            if (!isDragging) return;
            
            isDragging = false;
            handle.style.cursor = 'grab';
            
            // Rozpocznij powrót do środka
            returnToCenter();
        }
        
        function onMove(clientY) {
            if (!isDragging) return;
            
            const rect = wrapper.getBoundingClientRect();
            let y = clientY - rect.top - centerY;
            
            // Ogranicz do zakresu
            if (Math.abs(y) > maxDistance) {
                y = y > 0 ? maxDistance : -maxDistance;
            }
            
            currentY = y;
            updateHandlePosition(y);
            
            // Zaktualizuj wyświetlanie
            const normalized = normalizeValue(y);
            const angle = valueToAngle(normalized);
            
            displayValue.textContent = normalized.toFixed(2);
            displayAngle.textContent = angle;
            
            // Wyślij dane
            sendSliderData(normalized);
        }
        
        // Event listeners - mysz
        handle.addEventListener('mousedown', startDragging);
        document.addEventListener('mouseup', stopDragging);
        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                onMove(e.clientY);
            }
        });
        
        // Event listeners - dotyk
        handle.addEventListener('touchstart', (e) => {
            startDragging(e);
        });
        document.addEventListener('touchend', stopDragging);
        document.addEventListener('touchmove', (e) => {
            if (isDragging && e.touches.length > 0) {
                onMove(e.touches[0].clientY);
                e.preventDefault();
            }
        });
        
    })();

    // Udostępnij funkcję sendCommand globalnie dla innych przycisków
    window.sendCommand = sendCommand;



});