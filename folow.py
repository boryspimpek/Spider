import math
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

def move_servo(end_pos, steps=3, delay=0.01):
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


# Parametry chodu
STEP_COUNT = 3  # Liczba kroków w cyklu
x_amp = 30
z_amp = 40
offset_front = -5
offset_back = 15


for cycle in range(10):  
    print(f"Cykl chodu {cycle + 1}")
    
    for i in range(STEP_COUNT):
        # LF i RB w swing
        coxaLF = 90 + offset_front + i * (x_amp/STEP_COUNT)
        femurLF = 60 + z_amp * math.sin(i * math.pi / STEP_COUNT)

        coxaRB = 90 + offset_back + x_amp - i * (x_amp/STEP_COUNT)
        femurRB = 60 + z_amp * math.sin(i * math.pi / STEP_COUNT)

        # RF i LB w stance
        coxaRF = 90 - offset_front - x_amp + i * (x_amp/STEP_COUNT)
        femurRF = 120

        coxaLB = 90 - offset_back - i * (x_amp/STEP_COUNT)
        femurLB = 120

        print(f"Faza 1 - krok {i + 1}: coxaLF{coxaLF:.2f}, femurLF{femurLF:.2f} coxaRB{coxaRB:.2f}, femurRB{femurRB:.2f} | coxaRF{coxaRF:.2f}, femurRF{femurRF:.2f} coxaLB{coxaLB:.2f}, femurLB{femurLB:.2f}")
        move_servo({
            1: int(coxaLF), 2: int(femurLF),     # LF
            3: int(coxaRF), 4: int(femurRF),     # RF
            11: int(coxaLB), 12: int(femurLB),   # LB  
            13: int(coxaRB), 14: int(femurRB)    # RB
        })

    for i in range(STEP_COUNT):
        # RF i LB w swing
        coxaRF = 90 - offset_front - i * (x_amp/STEP_COUNT)
        femurRF = 120 - z_amp * math.sin(i * math.pi / STEP_COUNT)

        coxaLB = 90 - offset_back - x_amp + i * (x_amp/STEP_COUNT)
        femurLB = 120 - z_amp * math.sin(i * math.pi / STEP_COUNT)

        # LF i RB w stance
        coxaLF = 90 + offset_front + x_amp - i * (x_amp/STEP_COUNT)
        femurLF = 60

        coxaRB = 90 + offset_back + i * (x_amp/STEP_COUNT)
        femurRB = 60
        
        print(f"Faza 2 - krok {i + 1}: coxaLF{coxaLF:.2f}, femurLF{femurLF:.2f} coxaRB{coxaRB:.2f}, femurRB{femurRB:.2f} | coxaRF{coxaRF:.2f}, femurRF{femurRF:.2f} coxaLB{coxaLB:.2f}, femurLB{femurLB:.2f}")
        move_servo({
            1: int(coxaLF), 2: int(femurLF),     # LF
            3: int(coxaRF), 4: int(femurRF),     # RF
            11: int(coxaLB), 12: int(femurLB),   # LB
            13: int(coxaRB), 14: int(femurRB)    # RB
        })
