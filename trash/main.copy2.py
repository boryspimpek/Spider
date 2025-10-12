import math
import socket
import json
import time
import threading
from octosnake import Oscillator  # Import z poprawionej biblioteki
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import defaultdict
import time

#  Servos:
#   _________   ________   _________
#  |(2)______)(1)      (3)(______(4)|
#  |__|       |   KAME   |       |__|
#             |          |
#             |          |
#             |          |
#   _________ |          | _________
#  |(12)______)(11)______(13)(______(14)|
#  |__|                          |__|
#                  /\
#                  |
#             USBs |


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
        
        self.osc = [Oscillator() for _ in range(8)]
        
        ref_time = time.time() * 1000
        for osc in self.osc:
            osc.ref_time = ref_time
            
    def walk(self, steps, T):
        x_amp = 15
        z_amp = 15
        high_z = -15
        front_x = -10
        back_x = -30
        
        period = [T, T/2, T, T/2, T, T/2, T, T/2]
        amplitude = [x_amp, z_amp, x_amp, z_amp, x_amp, z_amp, x_amp, z_amp]
        offset = [front_x, high_z, front_x, high_z, back_x, high_z, back_x, high_z]
        phase = [90, 270, 90, 270, 270, 270, 270, 270]

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
                plotter.update_plot(positions)          
                # self.set_servo(positions)
                time.sleep(0.02)
                
            except Exception as e:
                print(f"Błąd podczas chodzenia: {e}")
                break

kame = Kame()
plotter = ServoPlotter(show_servos=[3, 4])
# plotter = ServoPlotter(show_servos=[1, 3, 11, 13])
kame.walk(steps=4, T=2000)
plt.show()