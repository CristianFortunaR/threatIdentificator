import cv2
import socket
import numpy as np
import struct
from ultralytics import YOLO
import threading # Importa o módulo threading

# Parâmetros da conexão
IP_JETSON = '0.0.0.0'
PORT = 8000

# Carrega o modelo YOLOv5/8
# carregar o modelo treinado em maquina best.pt
model = YOLO('yolov8n.pt')

def handle_client(conn, addr):
    print(f"Conectado por {addr}")

    data_buffer = b''
    payload_size = struct.calcsize(">L")

    try:
        while True:
            while len(data_buffer) < payload_size:
                data = conn.recv(4096)
                if not data:
                    raise ConnectionError(f"Cliente {addr} desconectado.")
                data_buffer += data

            packed_size = data_buffer[:payload_size]
            data_buffer = data_buffer[payload_size:]
            frame_size = struct.unpack(">L", packed_size)[0]

            while len(data_buffer) < frame_size:
                data = conn.recv(4096)
                if not data:
                    raise ConnectionError(f"Cliente {addr} desconectado.")
                data_buffer += data

            frame_data = data_buffer[:frame_size]
            data_buffer = data_buffer[frame_size:]

            np_arr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                print(f"Frame inválido recebido de {addr}.")
                continue

            # Aplica detecção com YOLOv
            results = model(frame, verbose=False)[0]
            annotated_frame = results.plot()

            # Cada cliente terá sua própria janela de exibição
            cv2.imshow(f'Jetson - YOLOv Processando - Cliente {addr}', annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except ConnectionError as e:
        print(e)
    except Exception as e:
        print(f"Erro ao lidar com o cliente {addr}: {e}")
    finally:
        conn.close()
        cv2.destroyAllWindows() # Isso pode fechar todas as janelas, considere gerenciar melhor
        print(f"Conexão com {addr} encerrada.")

# Cria socket TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP_JETSON, PORT))
server_socket.listen(5) # Aumenta o backlog para 5 conexões pendentes

print(f"Aguardando conexões na porta {PORT}...")

try:
    while True:
        conn, addr = server_socket.accept() # Aceita uma nova conexão
        # Cria uma nova thread para lidar com o cliente
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.daemon = True # Define a thread como daemon para que ela termine quando o programa principal terminar
        client_thread.start() # Inicia a thread
except KeyboardInterrupt:
    print("Servidor encerrado por interrupção do usuário.")
finally:
    server_socket.close()
    cv2.destroyAllWindows()
    print("Servidor encerrado.")
