from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
import eventlet

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

# Store satellite state
satellite_state = {
    'connected': False,
    'last_telemetry': None,
    'adcs_status': None,
    'power_status': None
}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'connected': satellite_state['connected']})

@socketio.on('send_command')
def handle_command(data):
    # Process and forward command to satellite
    print(f'Received command: {data}')
    # Forward to satellite simulation (TCP connection)
    # TODO: Implement satellite communication

@socketio.on('telemetry')
def handle_telemetry(data):
    # Process telemetry data from satellite
    satellite_state['last_telemetry'] = data
    emit('telemetry_update', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
