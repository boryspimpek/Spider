# Parametry chodu
import math


STEP_COUNT = 6  # Liczba kroków w cyklu
x_amp = 30
z_amp = 40
offset_front = -5
offset_back = 15




kroki = []  # tu będziemy zbierać wyniki dla każdego kroku

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

    kroki.append((
        f"Faza 1 - krok {i + 1}",
        coxaLF, femurLF, coxaRF, femurRF, coxaLB, femurLB, coxaRB, femurRB
    ))

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

    kroki.append((
        f"Faza 2 - krok {i + 1}",
        coxaLF, femurLF, coxaRF, femurRF, coxaLB, femurLB, coxaRB, femurRB
    ))

# -- WYŚWIETLANIE WYNIKÓW --

for opis, LF_c, LF_f, RF_c, RF_f, LB_c, LB_f, RB_c, RB_f in kroki:
    print(f"{opis}: "
          f"LF(c={LF_c:.2f}, f={LF_f:.2f}) | "
          f"RF(c={RF_c:.2f}, f={RF_f:.2f}) | "
          f"LB(c={LB_c:.2f}, f={LB_f:.2f}) | "
          f"RB(c={RB_c:.2f}, f={RB_f:.2f})")
