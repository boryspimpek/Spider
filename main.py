import math
import socket
import json
import time
import threading
from octosnake import Oscillator  
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import defaultdict

ESP_IP = "192.168.4.1"
ESP_PORT = 8888
SERVO_PINS = [1, 3, 2, 4, 11, 13, 12, 14]
initial_positions = {1: 90, 2: 90, 3: 90, 4: 90, 11: 90, 12: 90, 13: 90, 14: 90}
trimm = {1: 8, 2: -6, 3: 0, 4: -12, 11: 3, 12: 1, 13: 0, 14: -3}

current_positions = initial_positions.copy()


class ServoPlotter:
    def __init__(self, show_servos=None):
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.servo_data = defaultdict(list)
        self.timestamps = []
        self.start_time = time.time()
        self.show_servos = show_servos  # Lista serw do pokazania, np. [1, 3, 11]
        
    def update_plot(self, positions):
        current_time = time.time() - self.start_time
        self.timestamps.append(current_time)
        
        # Aktualizuj dane dla wszystkich serw
        for servo_id in self.servo_data.keys():
            if servo_id in positions:
                self.servo_data[servo_id].append(positions[servo_id])
            else:
                if self.servo_data[servo_id]:
                    self.servo_data[servo_id].append(self.servo_data[servo_id][-1])
                else:
                    self.servo_data[servo_id].append(0)
        
        for servo_id, position in positions.items():
            if servo_id not in self.servo_data:
                self.servo_data[servo_id] = [0] * (len(self.timestamps) - 1)
                self.servo_data[servo_id].append(position)
        
        self.ax.clear()
        
        # Rysuj tylko wybrane serwa
        for servo_id, positions_list in self.servo_data.items():
            if self.show_servos is None or servo_id in self.show_servos:
                if len(positions_list) == len(self.timestamps):
                    self.ax.plot(self.timestamps, positions_list, 
                                label=f'Serwo {servo_id}', marker='o', markersize=3)
        
        self.ax.set_xlabel('Czas (s)')
        self.ax.set_ylabel('Pozycja serwa')
        self.ax.set_title('Pozycje serw w czasie')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.draw()
        plt.pause(0.01)

class Kame:
    def __init__(self, name='kame'):
        self._name = name
        self._stop_event = threading.Event()
        
        self.osc = [Oscillator() for _ in range(8)]
        
        ref_time = time.time() * 1000
        for osc in self.osc:
            osc.ref_time = ref_time
            
        # self.set_neutral_position()
    
    def set_servo(self, servos):
        global current_positions
        
        trimmed_servos = {}
        for channel, angle in servos.items():
            trimmed_servos[channel] = angle + trimm.get(channel, 0)

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(0.1)  
            command = json.dumps({"set_servo": trimmed_servos})
            sock.sendto(command.encode(), (ESP_IP, ESP_PORT))
            sock.close()
            
            current_positions.update(servos)
            
        except Exception as e:
            print(f"Błąd komunikacji z ESP: {e}")
        finally:
            sock.close()

    def move_servo(self, end_pos, steps=2, delay=0.001):
        global current_positions
        
        channels = end_pos.keys()
        start_pos = {ch: current_positions.get(ch, initial_positions[ch]) for ch in channels}
        
        for step in range(1, steps + 1):
            intermediate = {}
            for ch in channels:
                start = start_pos[ch]
                stop = end_pos[ch]
                val = start + (stop - start) * step / steps
                intermediate[ch] = int(val)
            self.set_servo(intermediate)
            time.sleep(delay)

    def reset_to_initial(self):
        self.move_servo(initial_positions)

    def walk_forward(self, steps=4, T=1000):
        x_amp = 15
        z_amp = 15
        high_z = -15
        front_x = -10
        back_x = -30
        
        period = [T, T/2, T, T/2, T, T/2, T, T/2]
        amplitude = [x_amp, z_amp, x_amp, z_amp, x_amp, z_amp, x_amp, z_amp]
        offset = [front_x, high_z, front_x, high_z, back_x, high_z, back_x, high_z]
        phase = [90, 270, 270, 270, 90, 270, 270, 270]


        for i in range(8):
            self.osc[i].period = period[i]
            self.osc[i].amplitude = amplitude[i]
            self.osc[i].phase = phase[i]
            self.osc[i].offset = offset[i]

        init_ref = time.time() * 1000
        final_time = init_ref + (T * steps)  
        
        for osc in self.osc:
            osc.ref_time = init_ref
            # osc.phase = 0  # RESETUJE FAZE
    
        while (time.time() * 1000) < final_time:
            current_time_ms = time.time() * 1000
            side = int((current_time_ms - init_ref) / (T / 2.0)) % 2
            
            try:
                for i in range(8):
                    self.osc[i].refresh()

                positions = {}
                
                positions[1] = 90 - self.osc[0].output
                positions[3] = 90 + self.osc[2].output
                positions[11] = 90 + self.osc[4].output  
                positions[13] = 90 - self.osc[6].output
                
                if side == 0:
                    positions[2] = 90 + self.osc[1].output
                    positions[14] = 90 + self.osc[7].output
                    positions[4] = 90 + 2 * z_amp
                    positions[12] = 90 + 2 * z_amp
                else:
                    positions[4] = 90 - self.osc[3].output
                    positions[12] = 90 - self.osc[5].output
                    positions[2] = 90 - 2 * z_amp
                    positions[14] = 90 - 2 * z_amp


                print(f"Pozycje serw: { {k: round(v) for k, v in positions.items()} }")   
                # plotter.update_plot(positions)   
                self.set_servo(positions)
                time.sleep(0.01)
                
            except Exception as e:
                print(f"Błąd podczas chodzenia: {e}")
                break
        
    def stop(self):
        self._stop_event.set()
        time.sleep(0.1)
        self.set_neutral_position()
        self._stop_event.clear()

    def walk_back():
        print("Chodzenie do tyłu - funkcja niezaimplementowana")

    def turn_left():
        print("Skręt w lewo - funkcja niezaimplementowana")
    
    def turn_right():
        print("Skręt w prawo - funkcja niezaimplementowana")

    def set_femur_from_joystick(self, x, y, max_angle_change=30):
        angle_x = y * max_angle_change # odwrócone osie y dla naturalnego ruchu
        angle_y = x * max_angle_change

        # Oblicz nowe kąty femur łącząc obie osie
        femur_angles = {
            2: int(60 - angle_y - angle_x),  # Lewy przód: y (przód/tył) + x (lewo/prawo)
            4 : int(120 - angle_y + angle_x),  # Prawy przód: y (przód/tył) + x (prawo/lewo)
            12 : int(120 + angle_y - angle_x),  # Lewy tył: y (tył/przód) + x (lewo/prawo)
            14 : int(60 + angle_y + angle_x)  # Prawy tył: y (tył/przód) + x (prawo/lewo)
        }

        femur_angles[2] = max(60, min(90, femur_angles[2]))
        femur_angles[4] = max(90, min(120, femur_angles[4]))
        femur_angles[12] = max(90, min(120, femur_angles[12]))
        femur_angles[14] = max(60, min(90, femur_angles[14]))

        # Ustaw nowe pozycje femur
        self.move_servo(femur_angles, steps=2, delay=0.02)

    def set_all_femur_from_slider(self, value, max_angle_change=30):
        angle_offset = -value * max_angle_change     # value od -1 do 1, więc odwracamy znak żeby góra zmniejszała kąt
        femur_angles = {
            2: int(60 + angle_offset),   # LF femur
            4: int(120 - angle_offset),   # RF femur
            12: int(120 - angle_offset),  # LB femur
            14: int(60 + angle_offset)   # RB femur
        }

        femur_angles[2] = max(60, min(90, femur_angles[2]))
        femur_angles[4] = max(90, min(120, femur_angles[4]))
        femur_angles[12] = max(90, min(120, femur_angles[12]))
        femur_angles[14] = max(60, min(90, femur_angles[14]))
 
        self.move_servo(femur_angles, steps=2, delay=0.02)


# kame = Kame()
# plotter = ServoPlotter(show_servos=[11, 12])

# kame.walk_forward()
# plt.show()