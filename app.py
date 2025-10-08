import time
from flask import Flask, render_template, jsonify
import threading
from main import walk_forward, walk_back, turn_right, turn_left, reset_to_initial

app = Flask(__name__)

walking_forward = False
walking_backward = False
turning_right = False
turning_left = False
walk_stop_event = threading.Event()
reset_in_progress = False

# Obsługa strony głównej
@app.route('/')
def index():
    return render_template('index.html')

def walk_forward_loop():
    global walking_forward, reset_in_progress
    walking_forward = True
    walk_stop_event.clear()
    
    while walking_forward and not walk_stop_event.is_set():
        walk_forward(walk_stop_event)
    
    while reset_in_progress:
        time.sleep(0.01)

def walk_back_loop():
    global walking_backward, reset_in_progress
    walking_backward = True
    walk_stop_event.clear()
    
    while walking_backward and not walk_stop_event.is_set():
        walk_back(walk_stop_event)
    
    while reset_in_progress:
        time.sleep(0.01)

def turn_right_loop():
    global turning_right, reset_in_progress
    turning_right = True
    walk_stop_event.clear()
    
    while turning_right and not walk_stop_event.is_set():
        turn_right(walk_stop_event)
    
    while reset_in_progress:
        time.sleep(0.01)

def turn_left_loop():
    global turning_left, reset_in_progress
    turning_left = True
    walk_stop_event.clear()
    
    while turning_left and not walk_stop_event.is_set():
        turn_left(walk_stop_event)
    
    while reset_in_progress:
        time.sleep(0.01)

# walk forward
@app.route('/walkforward')
def walkforward_start():
    global walking_forward, walking_backward, turning_right, reset_in_progress
    if not any([walking_forward, walking_backward, turning_right, turning_left]) and not reset_in_progress:
        threading.Thread(target=walk_forward_loop).start()
    return jsonify({'status': 'walk forward started'})

# walk back
@app.route('/walkback')
def walkback_start():
    global walking_forward, walking_backward, turning_right, reset_in_progress
    if not any([walking_forward, walking_backward, turning_right, turning_left]) and not reset_in_progress:
        threading.Thread(target=walk_back_loop).start()
    return jsonify({'status': 'walk back started'})

# turn right
@app.route('/turnright')
def turnright_start():
    global walking_forward, walking_backward, turning_right, reset_in_progress
    if not any([walking_forward, walking_backward, turning_right, turning_left]) and not reset_in_progress:
        threading.Thread(target=turn_right_loop).start()
    return jsonify({'status': 'turn right started'})

# turn left
@app.route('/turnleft')
def turnleft_start():
    global walking_forward, walking_backward, turning_left, reset_in_progress
    if not any([walking_forward, walking_backward, turning_left, turning_left]) and not reset_in_progress:
        threading.Thread(target=turn_left_loop).start()
    return jsonify({'status': 'turn left started'})

# stop all movements
@app.route('/stopwalk')
def stopwalk():
    global walking_forward, walking_backward, turning_right, turning_left, reset_in_progress
    
    if not any([walking_forward, walking_backward, turning_right, turning_left]):
        return jsonify({'status': 'not moving'})
        
    walking_forward = False
    walking_backward = False
    turning_right = False
    turning_left = False
    walk_stop_event.set()
    
    # Poczekaj chwilę na zakończenie aktualnej fazy ruchu
    time.sleep(0.1)
    
    # Dopiero teraz wykonaj reset
    reset_in_progress = True
    reset_to_initial()
    reset_in_progress = False
    
    return jsonify({'status': 'movement stopped'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)