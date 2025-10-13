import time
from flask import Flask, render_template, jsonify, request
import threading
from main import Kame

kame = Kame()

# Zmienna do kontroli chodzenia
walking_thread = None
stop_walking = False

app = Flask(__name__)


def walk_forward_continuous():
    """Funkcja do ciągłego chodzenia w osobnym wątku"""
    global stop_walking
    stop_walking = False
    
    while not stop_walking:
        kame.walk_forward(steps=1, T=1000)  # Jeden krok na raz
        if stop_walking:
            break

def walk_backward_continuous():
    """Funkcja do ciągłego chodzenia do tyłu w osobnym wątku"""
    global stop_walking
    stop_walking = False
    
    while not stop_walking:
        kame.walk_backward(steps=1, T=1000)  # Jeden krok do tyłu na raz
        if stop_walking:
            break

def turn_left_continuous():
    """Funkcja do ciągłego skręcania w lewo w osobnym wątku"""
    global stop_walking
    stop_walking = False
    
    while not stop_walking:
        kame.turn_left(steps=1, T=2000)  # Jeden krok skrętu na raz
        if stop_walking:
            break

def turn_right_continuous():
    """Funkcja do ciągłego skręcania w prawo w osobnym wątku"""
    global stop_walking
    stop_walking = False
    
    while not stop_walking:
        kame.turn_right(steps=1, T=2000)  # Jeden krok skrętu na raz
        if stop_walking:
            break

def stop_walk():
    """Zatrzymanie chodzenia"""
    global stop_walking, walking_thread
    stop_walking = True
    
    if walking_thread and walking_thread.is_alive():
        walking_thread.join(timeout=1.0)

# Obsługa strony głównej
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/joystick', methods=['POST'])
def joystick_control():
    try:
        data = request.get_json()
        x = float(data.get('x', 0))
        y = float(data.get('y', 0))
        
        # Opcjonalnie: maksymalna zmiana kąta
        max_angle = int(data.get('max_angle', 30))
        
        # Wywołaj funkcję z main.py
        kame.set_femur_from_joystick(x, y, max_angle_change=max_angle)
        
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
    try:
        data = request.get_json()
        value = float(data.get('value', 0))
        
        # Opcjonalnie: maksymalna zmiana kąta
        max_angle = int(data.get('max_angle', 30))
        
        # Wywołaj funkcję z main.py
        kame.set_all_femur_from_slider(value, max_angle_change=max_angle)
        
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

@app.route('/walkforward')
def walk_forward():
    """Rozpocznij chodzenie do przodu"""
    try:
        global walking_thread, stop_walking
        
        # Zatrzymaj poprzednie chodzenie jeśli trwa
        stop_walk()
        
        # Ustaw flagę i uruchom nowy wątek
        stop_walking = False
        walking_thread = threading.Thread(target=walk_forward_continuous)
        walking_thread.daemon = True
        walking_thread.start()
        
        return jsonify({
            'status': 'walking_forward',
            'message': 'Rozpoczęto chodzenie do przodu'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Błąd chodzenia: {str(e)}'
        }), 500

@app.route('/walkbackward')
def walk_backward():
    """Rozpocznij chodzenie do tyłu"""
    try:
        global walking_thread, stop_walking
        
        # Zatrzymaj poprzednie chodzenie jeśli trwa
        stop_walk()
        
        # Ustaw flagę i uruchom nowy wątek
        stop_walking = False
        walking_thread = threading.Thread(target=walk_backward_continuous)
        walking_thread.daemon = True
        walking_thread.start()
        
        return jsonify({
            'status': 'walking_backward',
            'message': 'Rozpoczęto chodzenie do tyłu'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Błąd chodzenia: {str(e)}'
        }), 500

@app.route('/stopwalk')
def stop_walk_endpoint():
    """Zatrzymaj chodzenie"""
    try:
        stop_walk()
        
        return jsonify({
            'status': 'stopped',
            'message': 'Zatrzymano chodzenie'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Błąd zatrzymywania: {str(e)}'
        }), 500

@app.route('/turnleft')
def turn_left():
    """Wykonaj skręt w lewo"""
    try:
        global walking_thread, stop_walking
        # Zatrzymaj poprzednie chodzenie jeśli trwa
        stop_walk()

        # Ustaw flage i uruchom nowy wątek
        stop_walking = False
        walking_thread = threading.Thread(target=turn_left_continuous)
        walking_thread.daemon = True    
        walking_thread.start()
        return jsonify({
            'status': 'turning_left',
            'message': 'Wykonano skręt w lewo'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Błąd skrętu: {str(e)}'
        }), 500

@app.route('/turnright')
def turn_right():
    """Wykonaj skręt w prawo"""
    try:
        global walking_thread, stop_walking
        # Zatrzymaj poprzednie chodzenie jeśli trwa
        stop_walk()

        # Ustaw flage i uruchom nowy wątek
        stop_walking = False
        walking_thread = threading.Thread(target=turn_right_continuous)
        walking_thread.daemon = True    
        walking_thread.start()
        return jsonify({
            'status': 'turning_right',
            'message': 'Wykonano skręt w prawo'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Błąd skrętu: {str(e)}'
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)