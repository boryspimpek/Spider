import time
from flask import Flask, render_template, jsonify, request
import threading
from main import Kame

kame = Kame()

# Zmienne do kontroli ruchu
movement_thread = None
stop_movement = False

app = Flask(__name__)

def continuous_movement(direction):
    """Uproszczona funkcja ciągłego ruchu"""
    global stop_movement
    stop_movement = False

    while not stop_movement:
        kame.move(direction=direction, steps=1, T=2000)
        if stop_movement:
            break

def stop_movement_func():
    """Zatrzymanie ruchu"""
    global stop_movement, movement_thread
    stop_movement = True

    if movement_thread and movement_thread.is_alive():
        movement_thread.join(timeout=1.0)

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
        max_angle = int(data.get('max_angle', 30))

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
        max_angle = int(data.get('max_angle', 30))

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

@app.route('/move/<direction>')
def move_robot(direction):
    try:
        global movement_thread, stop_movement

        valid_directions = ['forward', 'backward', 'left', 'right']

        if direction not in valid_directions:
            return jsonify({
                'status': 'error',
                'message': f'Nieznany kierunek: {direction}'
            }), 400

        stop_movement_func()

        stop_movement = False
        movement_thread = threading.Thread(
            target=continuous_movement, 
            args=(direction,)  # Tylko kierunek
        )
        movement_thread.daemon = True
        movement_thread.start()

        return jsonify({
            'status': f'moving_{direction}',
            'message': f'Rozpoczęto ruch: {direction}',
            'direction': direction
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Błąd ruchu: {str(e)}'}), 500
    
@app.route('/stop')
def stop_movement_endpoint():
    """Zatrzymaj ruch"""
    try:
        stop_movement_func()
        return jsonify({
            'status': 'stopped',
            'message': 'Zatrzymano ruch'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Błąd zatrzymywania: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)