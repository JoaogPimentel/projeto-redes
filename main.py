from flask import Flask, jsonify, send_from_directory, request
import socket
import threading
import time

app = Flask(__name__, static_folder='static', static_url_path='')

SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999
INTERVAL = 1  # segundos entre pacotes

# Métricas
latencies, jitters, throughputs = [], [], []
last_latency = None
total_sent = 0
total_received = 0

# Estados globais
selected_protocol = "UDP"
server_thread_obj = None
client_thread_obj = None
server_running = False
client_running = False
server_socket = None  # para fechar corretamente na troca

# === Servidor TCP ou UDP ===
def start_server(protocol):
    def udp_server():
        global server_socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((SERVER_IP, SERVER_PORT))
        print(f"[UDP] Servidor rodando em {SERVER_IP}:{SERVER_PORT}")
        while server_running:
            try:
                data, addr = server_socket.recvfrom(1024)
                server_socket.sendto(data, addr)
            except:
                break
        server_socket.close()

    def tcp_server():
        global server_socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen(1)
        print(f"[TCP] Servidor rodando em {SERVER_IP}:{SERVER_PORT}")
        while server_running:
            try:
                conn, addr = server_socket.accept()
                with conn:
                    while server_running:
                        data = conn.recv(1024)
                        if not data:
                            break
                        conn.sendall(data)
            except:
                break
        server_socket.close()

    global server_thread_obj, server_running
    server_running = True
    server_thread_obj = threading.Thread(
        target=udp_server if protocol == "UDP" else tcp_server, daemon=True)
    server_thread_obj.start()

# === Cliente TCP ou UDP ===
def start_client(protocol):
    def run_client():
        global latencies, jitters, throughputs
        global last_latency, total_sent, total_received
        while client_running:
            try:
                if protocol == "UDP":
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                else:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(3)
                    sock.connect((SERVER_IP, SERVER_PORT))

                message = b"ping" * 64
                start_time = time.time()
                total_sent += 1

                if protocol == "UDP":
                    sock.sendto(message, (SERVER_IP, SERVER_PORT))
                    sock.settimeout(2)
                    data, _ = sock.recvfrom(1024)
                else:
                    sock.send(message)
                    data = sock.recv(1024)

                total_received += 1
                end_time = time.time()
                latency = round((end_time - start_time) * 1000, 2)
                latencies.append(latency)

                if last_latency is not None:
                    jitter = abs(latency - last_latency)
                    jitters.append(round(jitter, 2))
                last_latency = latency

                throughput = len(data) / INTERVAL
                throughputs.append(round(throughput / 1024, 2))

                # Limitar histórico
                latencies[:] = latencies[-100:]
                jitters[:] = jitters[-100:]
                throughputs[:] = throughputs[-100:]

            except Exception as e:
                print(f"[{protocol}] Erro cliente:", e)

            time.sleep(INTERVAL)

    global client_thread_obj, client_running
    client_running = True
    client_thread_obj = threading.Thread(target=run_client, daemon=True)
    client_thread_obj.start()

# === Rotas do Flask ===

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/metrics')
def metrics():
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0
    avg_jitter = round(sum(jitters) / len(jitters), 2) if jitters else 0
    avg_throughput = round(sum(throughputs) / len(throughputs), 2) if throughputs else 0
    packet_loss = round(((total_sent - total_received) / total_sent) * 100, 2) if total_sent > 0 else 0.0

    return jsonify({
        "latency": latencies[-20:],
        "jitter": jitters[-20:],
        "throughput": throughputs[-20:],
        "average_latency": avg_latency,
        "average_jitter": avg_jitter,
        "average_throughput": avg_throughput,
        "packet_loss_percent": packet_loss
    })

@app.route('/set_protocol', methods=['POST'])
def set_protocol():
    global selected_protocol, latencies, jitters, throughputs, last_latency
    global total_sent, total_received, server_running, client_running, server_socket

    data = request.get_json()
    protocol = data.get("protocol", "UDP").upper()

    if protocol not in ("UDP", "TCP"):
        return jsonify({"error": "Protocolo inválido"}), 400

    print(f"[INFO] Mudando protocolo para {protocol}")

    # Parar anteriores
    server_running = False
    client_running = False
    time.sleep(1)

    # Fechar socket antigo
    if server_socket:
        try:
            server_socket.close()
        except:
            pass
        server_socket = None

    # Resetar métricas
    selected_protocol = protocol
    latencies.clear()
    jitters.clear()
    throughputs.clear()
    last_latency = None
    total_sent = 0
    total_received = 0

    # Iniciar novamente
    start_server(protocol)
    start_client(protocol)

    return jsonify({"status": "ok", "protocol": protocol})

# Início
if __name__ == '__main__':
    start_server(selected_protocol)
    start_client(selected_protocol)
    app.run(debug=True, port=5000)
