import socket
import json
import time

# ZMIEŃ NA ADRES IP SWOJEGO ESP8266
ESP_IP = "192.168.4.1"
ESP_PORT = 8888

# Pozycje początkowe serw
initial_positions = {
    1: 90, 2: 90, 3: 90, 4: 90,
    11: 90, 12: 90, 13: 90, 14: 90
}

# Aktualne pozycje serw (inicjalizowane pozycjami początkowymi)
current_positions = initial_positions.copy()

trimm = {
    1: 3,
    2: 5,
    3: 3,
    4: -5,  
    11: 0,
    12: 3,
    13: -5,
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
        print(f"Wysyłam: {command}")
        
        sock.sendto(command.encode(), (ESP_IP, ESP_PORT))
        response, _ = sock.recvfrom(1024)
        print(f"Odpowiedź: {response.decode()}")
        
        # Zaktualizuj aktualne pozycje
        current_positions.update(servos)
        
    except Exception as e:
        print(f"Błąd: {e}")
    finally:
        sock.close()

def move_servo(end_pos, steps=5, delay=0.01):
    global current_positions
    
    channels = end_pos.keys()
    # Użyj aktualnych pozycji jako punkt startowy
    start_pos = {ch: current_positions.get(ch, initial_positions[ch]) for ch in channels}
    
    for step in range(1, steps + 1):
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

def walk():
    move_servo({1:90, 2:130, 3:120, 4:60, 11:130, 12:90, 13:60, 14:120})
    time.sleep(0.5)

    for i in range(5):
        # Faza 1
        move_servo({1:70, 2:110, 3:60, 11:110, 12:70, 14:60})
        # Faza 2
        move_servo({1:50, 2:90, 3:120, 11:90, 12:50, 14:120})
        # Faza 3
        move_servo({1:70, 2:110, 4:120, 11:110, 12:70, 13:120})
        # Faza 4
        move_servo({1:90, 2:130, 4:60, 11:130, 12:90, 13:60})
    
def test_servos():
    move_servo({1:100})
    time.sleep(2)
    move_servo({2:100})
    time.sleep(2)
    move_servo({3:100})
    time.sleep(2)
    move_servo({4:100})
    time.sleep(2)
    move_servo({11:100})
    time.sleep(2)
    move_servo({12:100})
    time.sleep(2)
    move_servo({13:100})
    time.sleep(2)
    move_servo({14:100})
    time.sleep(2)
