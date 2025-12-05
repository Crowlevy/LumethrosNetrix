from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
import sys
import os

#adiciona o diretório pai ao path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Utils.HostDetector import detect_live_hosts
from Utils.ui import Colors

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

#variável global para controlar o thread de background
monitoring_active = False

def background_scan(interface):
    """thread que executa o scan periodicamente e envia updates via websocket"""
    global monitoring_active
    print(f"{Colors.BRIGHT_GREEN}[WEB] Iniciando monitoramento em background...{Colors.RESET}")
    
    while monitoring_active:
        try:
            #detecta hosts (usando um ip local genérico para descobrir a rede)
            #em produção, idealmente passaria o ip local correto
            import socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                #não precisa ser alcançável
                s.connect(('10.255.255.255', 1))
                local_ip = s.getsockname()[0]
            except Exception:
                local_ip = '127.0.0.1'
            finally:
                s.close()

            #executa o scan (silencioso para não poluir o terminal do flask)
            #precisamos adaptar o hostdetector para não imprimir tanto ou capturar a saída
            #por enquanto, vamos chamar direto e deixar imprimir no console do servidor
            
            hosts = detect_live_hosts(local_ip, interface)
            
            #envia dados para o frontend
            socketio.emit('network_update', {'hosts': hosts, 'timestamp': time.strftime('%H:%M:%S')})
            
            #espera 30 segundos antes do próximo scan
            time.sleep(30)
            
        except Exception as e:
            print(f"{Colors.RED}[WEB] Erro no scan de background: {e}{Colors.RESET}")
            time.sleep(10)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_scan')
def start_scan_api():
    #endpoint para forçar um scan imediato (opcional)
    return jsonify({"status": "Scan iniciado"})

def start_web_server(interface=None):
    global monitoring_active
    monitoring_active = True
    
    #inicia thread de background
    bg_thread = threading.Thread(target=background_scan, args=(interface,))
    bg_thread.daemon = True
    bg_thread.start()
    
    print(f"{Colors.BRIGHT_CYAN}Dashboard acessível em: http://localhost:5000{Colors.RESET}")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
