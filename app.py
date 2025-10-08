# app.py
import time
from flask import Flask, render_template, jsonify
import threading
from main import walk, reset_to_initial

app = Flask(__name__)

walking = False
walk_stop_event = threading.Event()
reset_in_progress = False  # Nowa flaga

# Obsługa strony głównej
@app.route('/')
def index():
    return render_template('index.html')

def walk_loop():
    global walking, reset_in_progress
    walking = True
    walk_stop_event.clear()
    
    while walking and not walk_stop_event.is_set():
        walk(walk_stop_event)
    
    # Poczekaj aż reset się zakończy zanim wątek się zakończy
    while reset_in_progress:
        time.sleep(0.01)

# walk forward
@app.route('/walkforward/start')
def walkforward_start():
    global walking, reset_in_progress
    if not walking and not reset_in_progress:
        threading.Thread(target=walk_loop).start()
    return jsonify({'status': 'walk started'})

# stop walk
@app.route('/stopwalk')
def stopwalk():
    global walking, reset_in_progress
    
    if not walking:
        return jsonify({'status': 'not walking'})
        
    walking = False
    walk_stop_event.set()
    
    # Poczekaj chwilę na zakończenie aktualnej fazy chodu
    time.sleep(0.1)
    
    # Dopiero teraz wykonaj reset
    reset_in_progress = True
    reset_to_initial()
    reset_in_progress = False
    
    return jsonify({'status': 'walk stopped'})

if __name__ == '__main__':
    app.run(debug=True)