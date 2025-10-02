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

for cycle in range(6):  # Wykonaj 3 cykle chodu
    print(f"Cykl chodu {cycle + 1}")
    
    for i in range(STEP_COUNT):
        ############### FAZA 1 #################
        # LF i RB w fazie SWING (podnoszą się)
        coxaLF = 90 + i * (40/STEP_COUNT)        # LF przesuwa sie 
        femurLF = 70 + 35 * math.sin(i * math.pi/STEP_COUNT)   # podnosi się i opuszcza
        
        coxaRB = 130 - i * (40/STEP_COUNT)       # RB przesuwa sie   
        femurRB = 70 + 35 * math.sin(i * math.pi/STEP_COUNT)   # podnosi się i opuszcza

        # RF i LB w fazie stance (na ziemi)
        coxaRF = 50 + i * (40/STEP_COUNT)        # RF przesuwa się 
        femurRF = 110                             # na ziemi

        coxaLB = 90 - i * (40/STEP_COUNT)        # LB przesuwa się 
        femurLB = 110                             # na ziemi

        print(f"Faza 1 - krok {i + 1}: coxaLF({coxaLF:.2f}, femurLF{femurLF:.2f}) coxaRB({coxaRB:.2f}, femurRB{femurRB:.2f}) | coxaRF({coxaRF:.2f}, femurRF{femurRF:.2f}) coxaLB({coxaLB:.2f}, femurLB{femurLB:.2f})")
        move_servo({
            1: int(coxaLF), 2: int(femurLF),     # LF
            3: int(coxaRF), 4: int(femurRF),     # RF
            11: int(coxaLB), 12: int(femurLB),   # LB  
            13: int(coxaRB), 14: int(femurRB)    # RB
        })

    for i in range(STEP_COUNT):
        ################ FAZA 2 #################
        # LF i RB w fazie stance (na ziemi)
        coxaLF = 130 - i * (40/STEP_COUNT)       # LF przesuwa sie 
        femurLF = 70                             # na ziemi

        coxaRB = 90 + i * (40/STEP_COUNT)        # RB przesuwa sie 
        femurRB = 70                             # na ziemi

        # RF i LB w fazie SWING (podnoszą się)
        coxaRF = 90 - i * (40/STEP_COUNT)        # RF przesuwa się 
        femurRF = 110 - 35 * math.sin(i * math.pi/STEP_COUNT)   # podnosi się i opuszcza

        coxaLB = 50 + i * (40/STEP_COUNT)        # LB przesuwa się 
        femurLB = 110 - 35 * math.sin(i * math.pi/STEP_COUNT)   # podnosi się i opuszcza
        
        print(f"Faza 1 - krok {i + 1}: coxaLF({coxaLF:.2f}, femurLF{femurLF:.2f}) coxaRB({coxaRB:.2f}, femurRB{femurRB:.2f}) | coxaRF({coxaRF:.2f}, femurRF{femurRF:.2f}) coxaLB({coxaLB:.2f}, femurLB{femurLB:.2f})")
        move_servo({
            1: int(coxaLF), 2: int(femurLF),     # LF
            3: int(coxaRF), 4: int(femurRF),     # RF
            11: int(coxaLB), 12: int(femurLB),   # LB
            13: int(coxaRB), 14: int(femurRB)    # RB
        })
