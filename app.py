import time
from flask import Flask, render_template, jsonify, request
import threading
from main import walk_forward, walk_back, turn_right, turn_left, set_femur_from_joystick, set_all_femur_from_slider, reset_to_initial

app = Flask(__name__)

# Stan aplikacji
movement_states = {
    'forward': False,
    'backward': False,
    'right': False,
    'left': False
}

walk_stop_event = threading.Event()
reset_in_progress = False

# Mapowanie ruchów na funkcje
movement_functions = {
    'forward': walk_forward,
    'backward': walk_back,
    'right': turn_right,
    'left': turn_left
}

# Szablon pętli ruchu
def movement_loop(movement_type):
    global reset_in_progress
    movement_states[movement_type] = True
    walk_stop_event.clear()
    movement_func = movement_functions[movement_type]
    
    # Główna pętla ruchu
    while movement_states[movement_type] and not walk_stop_event.is_set():
        movement_func(walk_stop_event)
    
    # Oczekiwanie na zakończenie resetu
    while reset_in_progress:
        time.sleep(0.01)

# Sprawdzanie czy jakikolwiek ruch jest aktywny
def is_any_movement_active():
    return any(movement_states.values())

# Reset stanów ruchu
def reset_movement_states():
    for key in movement_states:
        movement_states[key] = False

# Obsługa strony głównej
@app.route('/')
def index():
    return render_template('index.html')

# Endpointy dla poszczególnych ruchów
@app.route('/walkforward')
def walkforward_start():
    global reset_in_progress
    if not is_any_movement_active() and not reset_in_progress:
        threading.Thread(target=movement_loop, args=('forward',)).start()
    return jsonify({'status': 'walk forward started'})

@app.route('/walkback')
def walkback_start():
    global reset_in_progress
    if not is_any_movement_active() and not reset_in_progress:
        threading.Thread(target=movement_loop, args=('backward',)).start()
    return jsonify({'status': 'walk back started'})

@app.route('/turnright')
def turnright_start():
    global reset_in_progress
    if not is_any_movement_active() and not reset_in_progress:
        threading.Thread(target=movement_loop, args=('right',)).start()
    return jsonify({'status': 'turn right started'})

@app.route('/turnleft')
def turnleft_start():
    global reset_in_progress
    if not is_any_movement_active() and not reset_in_progress:
        threading.Thread(target=movement_loop, args=('left',)).start()
    return jsonify({'status': 'turn left started'})

# Zatrzymanie wszystkich ruchów
@app.route('/stopwalk')
def stopwalk():
    global reset_in_progress
    
    if not is_any_movement_active():
        return jsonify({'status': 'not moving'})
        
    reset_movement_states()
    walk_stop_event.set()
    
    # Poczekaj chwilę na zakończenie aktualnej fazy ruchu
    time.sleep(0.1)
    
    # Dopiero teraz wykonaj reset
    reset_in_progress = True
    reset_to_initial()
    reset_in_progress = False
    
    return jsonify({'status': 'movement stopped'})

@app.route('/joystick', methods=['POST'])
def joystick_control():
    """
    Endpoint do kontroli femur przez joystick.
    Oczekuje JSON z polami: x, y (wartości od -1 do 1)
    """
    try:
        data = request.get_json()
        x = float(data.get('x', 0))
        y = float(data.get('y', 0))
        
        # Opcjonalnie: maksymalna zmiana kąta
        max_angle = int(data.get('max_angle', 30))
        
        # Wywołaj funkcję z main.py
        set_femur_from_joystick(x, y, max_angle_change=max_angle)
        
        return jsonify({
            'status': 'success',
            'x': x,
            'y': y,
            'message': f'Joystick: ({x:.2f}, {y:.2f})'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Błąd joysticka: {str(e)}'
        }), 500

@app.route('/slider', methods=['POST'])
def slider_control():
    """
    Endpoint do kontroli wszystkich femur jednocześnie przez slider.
    Oczekuje JSON z polem: value (wartość od -1 do 1, gdzie 0 to środek/90°)
    """
    try:
        data = request.get_json()
        value = float(data.get('value', 0))
        
        # Opcjonalnie: maksymalna zmiana kąta
        max_angle = int(data.get('max_angle', 30))
        
        # Wywołaj funkcję z main.py
        set_all_femur_from_slider(value, max_angle_change=max_angle)
        
        return jsonify({
            'status': 'success',
            'value': value,
            'message': f'Slider: {value:.2f}'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Błąd slidera: {str(e)}'
        }), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)