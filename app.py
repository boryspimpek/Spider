import time
from flask import Flask, render_template, jsonify
import threading
from main import walk_forward, walk_back, reset_to_initial

app = Flask(__name__)

walking_forward = False
walking_backward = False
walk_stop_event = threading.Event()
reset_in_progress = False  # Nowa flaga

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
    
    # Poczekaj aż reset się zakończy zanim wątek się zakończy
    while reset_in_progress:
        time.sleep(0.01)

def walk_back_loop():
    global walking_backward, reset_in_progress
    walking_backward = True
    walk_stop_event.clear()
    
    while walking_backward and not walk_stop_event.is_set():
        walk_back(walk_stop_event)
    
    # Poczekaj aż reset się zakończy zanim wątek się zakończy
    while reset_in_progress:
        time.sleep(0.01)

# walk forward
@app.route('/walkforward')
def walkforward_start():
    global walking_forward, walking_backward, reset_in_progress
    if not walking_forward and not walking_backward and not reset_in_progress:
        threading.Thread(target=walk_forward_loop).start()
    return jsonify({'status': 'walk forward started'})

# walk back
@app.route('/walkback')
def walkback_start():
    global walking_forward, walking_backward, reset_in_progress
    if not walking_forward and not walking_backward and not reset_in_progress:
        threading.Thread(target=walk_back_loop).start()
    return jsonify({'status': 'walk back started'})

# stop walk
@app.route('/stopwalk')
def stopwalk():
    global walking_forward, walking_backward, reset_in_progress
    
    if not walking_forward and not walking_backward:
        return jsonify({'status': 'not walking'})
        
    walking_forward = False
    walking_backward = False
    walk_stop_event.set()
    
    # Poczekaj chwilę na zakończenie aktualnej fazy chodu
    time.sleep(0.1)
    
    # Dopiero teraz wykonaj reset
    reset_in_progress = True
    reset_to_initial()
    reset_in_progress = False
    
    return jsonify({'status': 'walk stopped'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)