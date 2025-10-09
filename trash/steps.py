# Parametry chodu
import math



step_count=4
x_amp=20
z_amp=30
offset_front=5
offset_back=15
offset_turn=10
offset_z = 30



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


walk_forward()