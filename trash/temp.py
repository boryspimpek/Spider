import math
import socket
import json
import time

# ZMIEŃ NA ADRES IP SWOJEGO ESP8266
ESP_IP = "192.168.4.1"
ESP_PORT = 8888

# Pozycje początkowe serw
initial_positions = {
    1: 85, 2: 60, 
    3: 65, 4: 120,
    11: 75, 12: 120, 
    13: 135, 14: 60
    
}

# Aktualne pozycje serw (inicjalizowane pozycjami początkowymi)
current_positions = initial_positions.copy()

trimm = {
    1: 3,
    2: -5,
    3: 0,
    4: -8,  
    11: -10,
    12: 2,
    13: 20,
    14: -5
}

def set_servo(servos):
    global current_positions
    
    # Dodaj trim do każdego kanału
    trimmed_servos = {}
    for channel, angle in servos.items():
        trimmed_servos[channel] = angle + trimm.get(channel, 0)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)
    
    try:
        command = json.dumps({"set_servo": trimmed_servos})
        # print(f"Wysyłam: {command}")
        
        sock.sendto(command.encode(), (ESP_IP, ESP_PORT))
        response, _ = sock.recvfrom(1024)
        # print(f"Odpowiedź: {response.decode()}")
        
        # Zaktualizuj aktualne pozycje
        current_positions.update(servos)
        
    except Exception as e:
        print(f"Błąd: {e}")
    finally:
        sock.close()

def move_servo(end_pos, steps=3, delay=0.01, stop_event=None):
    global current_positions
    
    channels = end_pos.keys()
    start_pos = {ch: current_positions.get(ch, initial_positions[ch]) for ch in channels}
    
    for step in range(1, steps + 1):
        if stop_event and stop_event.is_set():  # Sprawdź w każdej iteracji
            return
            
        intermediate = {}
        for ch in channels:
            start = start_pos[ch]
            stop = end_pos[ch]
            val = start + (stop - start) * step / steps
            intermediate[ch] = int(val)
        set_servo(intermediate)
        time.sleep(delay)

def reset_to_initial():
    move_servo(initial_positions)



# Stałe konfiguracji - w kolejności: coxa, femur dla każdej nogi
SERVO_PARAMS = {
    "right": {
        # LF: coxa (1), femur (2)
        1: (90 + 10, 0.0),    # coxa_center, phase  
        2: (60, 0.0),         # femur_center, phase
        
        # RF: coxa (3), femur (4)  
        3: (90 - 10, 0.5),    # 180° out of phase
        4: (120, 0.5),
        
        # LB: coxa (11), femur (12)
        11: (90 - 10, 0.5),   # 180° out of phase
        12: (120, 0.5),
        
        # RB: coxa (13), femur (14)
        13: (90 + 10, 0.0),
        14: (60, 0.0)
    },
    "left": {
        # LF: coxa (1), femur (2)
        1: (90 + 10, 0.5),    # 180° out of phase
        2: (60, 0.5),
        
        # RF: coxa (3), femur (4)
        3: (90 - 10, 0.0),
        4: (120, 0.0),
        
        # LB: coxa (11), femur (12)
        11: (90 - 10, 0.0),
        12: (120, 0.0),
        
        # RB: coxa (13), femur (14)
        13: (90 + 10, 0.5),   # 180° out of phase
        14: (60, 0.5)
    }
}

def turn(direction="right", stop_event=None, x_amp=30, z_amp=30):
    params = SERVO_PARAMS[direction]
    frequency = 1.0  # Hz - częstotliwość kroku
    
    while not (stop_event and stop_event.is_set()):
        t = (time.time() * frequency) % 1.0  # faza 0-1
        positions = {}
        
        for servo_id, (center, phase) in params.items():
            phase_t = (t + phase) % 1.0  # faza z przesunięciem
            
            if servo_id % 2 == 1:  # coxa (nieparzyste ID: 1, 3, 11, 13)
                # Ruch coxa - trójkątny (przód/tył)
                if phase_t < 0.5:
                    value = center + x_amp * (1 - 4 * phase_t)  # 1 -> -1
                else:
                    value = center - x_amp * (4 * phase_t - 3)  # -1 -> 1
                positions[servo_id] = int(value)
                
            else:  # femur (parzyste ID: 2, 4, 12, 14)
                # Ruch femur - sinusoidalny (podnoszenie)
                if phase_t < 0.5:
                    value = center + z_amp * math.sin(phase_t * 2 * math.pi)
                else:
                    value = center
                positions[servo_id] = int(value)
        
        print(positions)
        time.sleep(0.02)  # 50Hz refresh rate
turn()