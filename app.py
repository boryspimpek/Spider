from flask import Flask, render_template, jsonify
import main  

app = Flask(__name__)

ACTIONS = {
    'test_servo': main.test_servo,
    # Add new actions here
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move/<action>')
def move_robot(action):
    try:
        if action in ACTIONS:
            ACTIONS[action]()
            return jsonify({
                'status': 'success', 
                'action': action,
                'message': f'Wykonano akcję: {action}'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Nieznana akcja: {action}'
            }), 400
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Błąd wykonania: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)