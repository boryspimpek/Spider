import math
import socket
import json
import time

# ZMIEŃ NA ADRES IP SWOJEGO ESP8266
ESP_IP = "192.168.4.1"
ESP_PORT = 8888

# Pozycje początkowe serw
initial_positions = {
    1: 115, 2: 60, 
    3: 65, 4: 120,
    11: 65, 12: 120, 
    13: 115, 14: 60
    
}

# Aktualne pozycje serw (inicjalizowane pozycjami początkowymi)
current_positions = initial_positions.copy()

trimm = {
    1: 8,
    2: -6,
    3: 0,
    4: -12,  
    11: 3,
    12: 1,
    13: 0,
    14: -3
}

# Parametry chodzenia
step_count=3
x_amp=30
z_amp=30
offset_front=-5
offset_back=15
offset_turn=10
offset_z = 30

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

def move_servo(end_pos, steps=2, delay=0.001, stop_event=None):
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

def walk_back(stop_event=None):
    for i in range(step_count):
        if stop_event and stop_event.is_set():  # Sprawdź czy przerwać
            return
                
        # LF i RB w stance
        coxaLF = 90 + offset_back + i * (x_amp/step_count)
        femurLF = 90 - offset_z  

        coxaRB = 90 + offset_front + x_amp - i * (x_amp/step_count)
        femurRB = 90 - offset_z 

        # RF i LB w swing
        coxaRF = 90 - offset_back - x_amp + i * (x_amp/step_count)
        femurRF = (90 + offset_z) - z_amp * math.sin(i * math.pi / step_count )

        coxaLB = 90 - offset_front - i * (x_amp/step_count)
        femurLB = (90 + offset_z) - z_amp * math.sin(i * math.pi / step_count)

        print(f"Faza 1 - krok {i + 1}: coxaLF{coxaLF:.2f}, femurLF{femurLF:.2f} coxaRB{coxaRB:.2f}, femurRB{femurRB:.2f} | coxaRF{coxaRF:.2f}, femurRF{femurRF:.2f} coxaLB{coxaLB:.2f}, femurLB{femurLB:.2f}")
        move_servo({
            1: int(coxaLF), 2: int(femurLF),     # LF
            3: int(coxaRF), 4: int(femurRF),     # RF
            11: int(coxaLB), 12: int(femurLB),   # LB  
            13: int(coxaRB), 14: int(femurRB)    # RB
        })

    for i in range(step_count):
        if stop_event and stop_event.is_set():  # Sprawdź czy przerwać
            return
                
        # RF i LB w stance
        coxaRF = 90 - offset_back - i * (x_amp/step_count)
        femurRF = (90 + offset_z) 

        coxaLB = 90 - offset_front - x_amp + i * (x_amp/step_count)
        femurLB = (90 + offset_z) 

        # LF i RB w swing
        coxaLF = 90 + offset_back + x_amp - i * (x_amp/step_count)
        femurLF = (90 - offset_z) + z_amp * math.sin(i * math.pi / step_count)

        coxaRB = 90 + offset_front + i * (x_amp/step_count)
        femurRB = (90 - offset_z) + z_amp * math.sin(i * math.pi / step_count)
        
        print(f"Faza 2 - krok {i + 1}: coxaLF{coxaLF:.2f}, femurLF{femurLF:.2f} coxaRB{coxaRB:.2f}, femurRB{femurRB:.2f} | coxaRF{coxaRF:.2f}, femurRF{femurRF:.2f} coxaLB{coxaLB:.2f}, femurLB{femurLB:.2f}")
        move_servo({
            1: int(coxaLF), 2: int(femurLF),     # LF
            3: int(coxaRF), 4: int(femurRF),     # RF
            11: int(coxaLB), 12: int(femurLB),   # LB
            13: int(coxaRB), 14: int(femurRB)    # RB
        })

def walk_forward(stop_event=None):
    for i in range(step_count):
        if stop_event and stop_event.is_set():  # Sprawdź czy przerwać
            return
                
        # LF i RB w swing
        coxaLF = 90 + offset_front + i * (x_amp/step_count)
        femurLF = (90 - offset_z) + z_amp * math.sin(i * math.pi / step_count)

        coxaRB = 90 + offset_back + x_amp - i * (x_amp/step_count)
        femurRB = (90 - offset_z) + z_amp * math.sin(i * math.pi / step_count)

        # RF i LB w stance
        coxaRF = 90 - offset_front - x_amp + i * (x_amp/step_count)
        femurRF = (90 + offset_z)

        coxaLB = 90 - offset_back - i * (x_amp/step_count)
        femurLB = (90 + offset_z)

        print(f"Faza 1 - krok {i + 1}: coxaLF{coxaLF:.2f}, femurLF{femurLF:.2f} coxaRB{coxaRB:.2f}, femurRB{femurRB:.2f} | coxaRF{coxaRF:.2f}, femurRF{femurRF:.2f} coxaLB{coxaLB:.2f}, femurLB{femurLB:.2f}")
        move_servo({
            1: int(coxaLF), 2: int(femurLF),     # LF
            3: int(coxaRF), 4: int(femurRF),     # RF
            11: int(coxaLB), 12: int(femurLB),   # LB  
            13: int(coxaRB), 14: int(femurRB)    # RB
        })

    for i in range(step_count):
        if stop_event and stop_event.is_set():  # Sprawdź czy przerwać
            return
                
        # RF i LB w swing
        coxaRF = 90 - offset_front - i * (x_amp/step_count)
        femurRF = (90 + offset_z) - z_amp * math.sin(i * math.pi / step_count)

        coxaLB = 90 - offset_back - x_amp + i * (x_amp/step_count)
        femurLB = (90 + offset_z) - z_amp * math.sin(i * math.pi / step_count)

        # LF i RB w stance
        coxaLF = 90 + offset_front + x_amp - i * (x_amp/step_count)
        femurLF = (90 - offset_z)

        coxaRB = 90 + offset_back + i * (x_amp/step_count)
        femurRB = (90 - offset_z)
        
        print(f"Faza 2 - krok {i + 1}: coxaLF{coxaLF:.2f}, femurLF{femurLF:.2f} coxaRB{coxaRB:.2f}, femurRB{femurRB:.2f} | coxaRF{coxaRF:.2f}, femurRF{femurRF:.2f} coxaLB{coxaLB:.2f}, femurLB{femurLB:.2f}")
        move_servo({
            1: int(coxaLF), 2: int(femurLF),     # LF
            3: int(coxaRF), 4: int(femurRF),     # RF
            11: int(coxaLB), 12: int(femurLB),   # LB
            13: int(coxaRB), 14: int(femurRB)    # RB
        })

def turn_right(stop_event=None):
    for i in range(step_count):
        if stop_event and stop_event.is_set():  # Sprawdź czy przerwać
            return
                
        # LF i RB w swing
        coxaLF = 90 + offset_turn + i * (x_amp/step_count)
        femurLF = (90 - offset_z) + z_amp * math.sin(i * math.pi / step_count)

        coxaRB = 90 + offset_front + i * (x_amp/step_count)
        femurRB = (90 - offset_z) + z_amp * math.sin(i * math.pi / step_count)

        # RF i LB w stance
        coxaRF = 90 - offset_turn - i * (x_amp/step_count)
        femurRF = (90 + offset_z)

        coxaLB = 90 - offset_turn - i * (x_amp/step_count)
        femurLB = (90 + offset_z)

        print(f"Faza 1 - krok {i + 1}: coxaLF{coxaLF:.2f}, femurLF{femurLF:.2f} coxaRB{coxaRB:.2f}, femurRB{femurRB:.2f} | coxaRF{coxaRF:.2f}, femurRF{femurRF:.2f} coxaLB{coxaLB:.2f}, femurLB{femurLB:.2f}")
        move_servo({
            1: int(coxaLF), 2: int(femurLF),     # LF
            3: int(coxaRF), 4: int(femurRF),     # RF
            11: int(coxaLB), 12: int(femurLB),   # LB  
            13: int(coxaRB), 14: int(femurRB)    # RB
        })

    for i in range(step_count):
        if stop_event and stop_event.is_set():  # Sprawdź czy przerwać
            return
                
        # RF i LB w swing
        coxaRF = 90 - offset_turn - x_amp + i * (x_amp/step_count)
        femurRF = (90 + offset_z) - z_amp * math.sin(i * math.pi / step_count)

        coxaLB = 90 - offset_turn - x_amp + i * (x_amp/step_count)
        femurLB = (90 + offset_z) - z_amp * math.sin(i * math.pi / step_count)

        # LF i RB w stance
        coxaLF = 90 + offset_turn + x_amp - i * (x_amp/step_count)
        femurLF = (90 - offset_z)

        coxaRB = 90 + offset_turn + x_amp - i * (x_amp/step_count)
        femurRB = (90 - offset_z)
        
        print(f"Faza 2 - krok {i + 1}: coxaLF{coxaLF:.2f}, femurLF{femurLF:.2f} coxaRB{coxaRB:.2f}, femurRB{femurRB:.2f} | coxaRF{coxaRF:.2f}, femurRF{femurRF:.2f} coxaLB{coxaLB:.2f}, femurLB{femurLB:.2f}")
        move_servo({
            1: int(coxaLF), 2: int(femurLF),     # LF
            3: int(coxaRF), 4: int(femurRF),     # RF
            11: int(coxaLB), 12: int(femurLB),   # LB
            13: int(coxaRB), 14: int(femurRB)    # RB
        })

def turn_left(stop_event=None):
    for i in range(step_count):
        if stop_event and stop_event.is_set():  # Sprawdź czy przerwać
            return
                
        # LF i RB w swing
        coxaLF = 90 + offset_turn + x_amp - i * (x_amp/step_count)
        femurLF = (90 - offset_z) + z_amp * math.sin(i * math.pi / step_count)

        coxaRB = 90 + offset_turn + x_amp - i * (x_amp/step_count)
        femurRB = (90 - offset_z) + z_amp * math.sin(i * math.pi / step_count)

        # RF i LB w stance
        coxaRF = 90 - offset_turn - x_amp + i * (x_amp/step_count)
        femurRF = (90 + offset_z)

        coxaLB = 90 - offset_turn - x_amp + i * (x_amp/step_count)
        femurLB = (90 + offset_z)

        print(f"Faza 1 - krok {i + 1}: coxaLF{coxaLF:.2f}, femurLF{femurLF:.2f} coxaRB{coxaRB:.2f}, femurRB{femurRB:.2f} | coxaRF{coxaRF:.2f}, femurRF{femurRF:.2f} coxaLB{coxaLB:.2f}, femurLB{femurLB:.2f}")
        move_servo({
            1: int(coxaLF), 2: int(femurLF),     # LF
            3: int(coxaRF), 4: int(femurRF),     # RF
            11: int(coxaLB), 12: int(femurLB),   # LB  
            13: int(coxaRB), 14: int(femurRB)    # RB
        })

    for i in range(step_count):
        if stop_event and stop_event.is_set():  # Sprawdź czy przerwać
            return
                
        # RF i LB w swing
        coxaRF = 90 - offset_turn - i * (x_amp/step_count)
        femurRF = (90 + offset_z) - z_amp * math.sin(i * math.pi / step_count)

        coxaLB = 90 - offset_turn - i * (x_amp/step_count)
        femurLB = (90 + offset_z) - z_amp * math.sin(i * math.pi / step_count)

        # LF i RB w stance
        coxaLF = 90 + offset_turn + i * (x_amp/step_count)
        femurLF = (90 - offset_z)

        coxaRB = 90 + offset_turn + i * (x_amp/step_count)
        femurRB = (90 - offset_z)
        
        print(f"Faza 2 - krok {i + 1}: coxaLF{coxaLF:.2f}, femurLF{femurLF:.2f} coxaRB{coxaRB:.2f}, femurRB{femurRB:.2f} | coxaRF{coxaRF:.2f}, femurRF{femurRF:.2f} coxaLB{coxaLB:.2f}, femurLB{femurLB:.2f}")
        move_servo({
            1: int(coxaLF), 2: int(femurLF),     # LF
            3: int(coxaRF), 4: int(femurRF),     # RF
            11: int(coxaLB), 12: int(femurLB),   # LB
            13: int(coxaRB), 14: int(femurRB)    # RB
        })

def set_femur_from_joystick(x, y, max_angle_change=30):
    angle_x = y * max_angle_change # odwrócone osie y dla naturalnego ruchu
    angle_y = x * max_angle_change

    # Oblicz nowe kąty femur łącząc obie osie
    femur_angles = {
        2: int(60 - angle_y - angle_x),  # Lewy przód: y (przód/tył) + x (lewo/prawo)
        4 : int(120 - angle_y + angle_x),  # Prawy przód: y (przód/tył) + x (prawo/lewo)
        12 : int(120 + angle_y - angle_x),  # Lewy tył: y (tył/przód) + x (lewo/prawo)
        14 : int(60 + angle_y + angle_x)  # Prawy tył: y (tył/przód) + x (prawo/lewo)
    }
    # Ustaw nowe pozycje femur
    move_servo(femur_angles, steps=2, delay=0.02)


def set_all_femur_from_slider(value, max_angle_change=30):
    angle_offset = -value * max_angle_change     # value od -1 do 1, więc odwracamy znak żeby góra zmniejszała kąt
    femur_angles = {
        2: int(60 + angle_offset),   # LF femur
        4: int(120 - angle_offset),   # RF femur
        12: int(120 - angle_offset),  # LB femur
        14: int(60 + angle_offset)   # RB femur
    }
    move_servo(femur_angles, steps=2, delay=0.02)



def prerare_walk():
    move_servo({
        1: 85, 2: 60, 
        3: 65, 4: 120,
        11: 75, 12: 120, 
        13: 135, 14: 60
    })




# move_servo({
#     1: 90, 2: 90,     # LF
#     3: 90, 4: 90,     # RF
#     11: 90, 12: 90,   # LB
#     13: 90, 14: 90    # RB
# })
