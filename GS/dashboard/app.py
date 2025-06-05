from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
import eventlet
from datetime import datetime
from pathlib import Path
import os
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')

# Caminho para os logs do satélite
LOGS_DIR = Path("/home/groundstation/projeto_final/GS/logs")

# Store satellite state
satellite_state = {
    'connected': False,
    'last_telemetry': None,
    'last_log_check': datetime.now().timestamp(),
    'adcs_status': None,
    'power_status': None
}

def read_log_file(category, filename):
    """Lê um arquivo de log JSON com histórico"""
    try:
        filepath = LOGS_DIR / category / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                logs = json.load(f)
                if isinstance(logs, list) and logs:
                    # Retorna a entrada mais recente por padrão
                    return logs[-1]  # Último item do array
                return logs
    except Exception as e:
        print(f"Erro ao ler {filepath}: {e}")
    return None

def get_log_history(category, filename, limit=50):
    """Obtém histórico completo de um arquivo de log"""
    try:
        filepath = LOGS_DIR / category / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                logs = json.load(f)
                if isinstance(logs, list):
                    # Limitar o número de entradas retornadas
                    return logs[-limit:] if len(logs) > limit else logs
                # Se não for uma lista, retorna como item único
                return [logs]
    except Exception as e:
        print(f"Erro ao ler histórico de {filepath}: {e}")
    return []

def check_for_signal():
    """Verifica se há comunicação com o satélite recentemente"""
    radio_log = read_log_file("communication", "radio.json")
    if radio_log and "timestamp" in radio_log:
        try:
            log_time = datetime.fromisoformat(radio_log["timestamp"])
            now = datetime.now()
            time_diff = (now - log_time).total_seconds()
            return time_diff < 30  # Considera conectado se o log tiver menos de 30 segundos
        except (ValueError, TypeError) as e:
            print(f"Erro ao analisar timestamp: {e}")
    return False

def gather_telemetry():
    """Background task que coleta telemetria dos logs e envia ao cliente"""
    while True:
        try:
            # Verificar se há comunicação recente com o satélite
            connected = check_for_signal()
            if satellite_state['connected'] != connected:
                satellite_state['connected'] = connected
                socketio.emit('status', {'connected': connected})
            
            # Coletar dados dos diferentes subsistemas
            telemetry = {
                'timestamp': datetime.now().isoformat(),
                'adcs': {
                    'attitude': read_log_file('adcs', 'attitude.json'),
                    'magnetometer': read_log_file('adcs', 'magnetometer.json')
                },
                'power': {
                    'battery': read_log_file('power', 'battery.json'),
                    'solar': read_log_file('power', 'solar_panels.json'),
                    'consumption': read_log_file('power', 'consumption.json')
                },
                'thermal': read_log_file('thermal', 'temperatures.json'),
                'communication': read_log_file('communication', 'radio.json'),
                'system': read_log_file('system', 'status.json')
            }
            
            satellite_state['last_telemetry'] = telemetry
            socketio.emit('telemetry_update', telemetry)
            
        except Exception as e:
            print(f"Erro ao coletar telemetria: {e}")
        finally:
            eventlet.sleep(1)  # Atualiza a cada segundo

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/history/<category>/<filename>')
def get_history(category, filename):
    """Endpoint para obter histórico de logs para gráficos"""
    history = get_log_history(category, filename, limit=100)
    return json.dumps(history)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'connected': satellite_state['connected']})
    if satellite_state['last_telemetry']:
        emit('telemetry_update', satellite_state['last_telemetry'])

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
    # Inicia a tarefa de coleta de telemetria em segundo plano
    socketio.start_background_task(gather_telemetry)
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)
