import cv2
import socket
import numpy as np
import struct
from ultralytics import YOLO
import threading

# Parâmetros da conexão
IP_JETSON = '0.0.0.0'
PORT = 8000

# Carrega o modelo YOLOv5/8
model = YOLO('yolov8n.pt')

# Dicionário para armazenar informações sobre cada cliente conectado
client_info = {}
client_window_names = {} # Para gerenciar nomes de janelas por cliente

def handle_client(conn, addr):
    client_address_str = f"{addr[0]}:{addr[1]}"
    print(f"Conectado por {client_address_str}")

    data_buffer = b''
    payload_size = struct.calcsize(">L")

    # Gera um nome de janela único para este cliente
    window_name = f'Jetson - YOLOv Processando - Cliente {client_address_str}'
    client_window_names[client_address_str] = window_name

    try:
        while True:
            while len(data_buffer) < payload_size:
                data = conn.recv(4096)
                if not data:
                    raise ConnectionError(f"Cliente {client_address_str} desconectado.")
                data_buffer += data

            packed_size = data_buffer[:payload_size]
            data_buffer = data_buffer[payload_size:]
            frame_size = struct.unpack(">L", packed_size)[0]

            while len(data_buffer) < frame_size:
                data = conn.recv(4096)
                if not data:
                    raise ConnectionError(f"Cliente {client_address_str} desconectado.")
                data_buffer += data

            frame_data = data_buffer[:frame_size]
            data_buffer = data_buffer[frame_size:]

            np_arr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                print(f"Frame inválido recebido de {client_address_str}.")
                continue

            # Aplica detecção com YOLOv
            results = model(frame, verbose=False)[0]
            annotated_frame = results.plot()


            detections_count = len(results.boxes)
            info_text = f"Objetos Detectados: {detections_count}"
            cv2.putText(annotated_frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

            detected_classes = [model.names[int(box.cls)] for box in results.boxes]
            if detected_classes:
                class_text = f"Classes: {', '.join(set(detected_classes))}"
                cv2.putText(annotated_frame, class_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)

            client_ip_text = f"Cliente IP: {addr[0]}"
            client_port_text = f"Cliente Porta: {addr[1]}"
            cv2.putText(annotated_frame, client_ip_text, (annotated_frame.shape[1] - 300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(annotated_frame, client_port_text, (annotated_frame.shape[1] - 300, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2, cv2.LINE_AA)


            cv2.imshow(window_name, annotated_frame)

            client_info[client_address_str] = {
                "last_frame_time": cv2.getTickCount(),
                "detections_count": detections_count,
                "detected_classes": detected_classes
            }

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except ConnectionError as e:
        print(e)
    except Exception as e:
        print(f"Erro ao lidar com o cliente {client_address_str}: {e}")
    finally:
        conn.close()
        if window_name in client_window_names.values():
            cv2.destroyWindow(window_name)
            del client_window_names[client_address_str] 
        print(f"Conexão com {client_address_str} encerrada.")

# Cria socket TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP_JETSON, PORT))
server_socket.listen(5)

print(f"Aguardando conexões na porta {PORT}...")

try:
    while True:
        conn, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.daemon = True
        client_thread.start()
except KeyboardInterrupt:
    print("Servidor encerrado por interrupção do usuário.")
finally:
    server_socket.close()
    # No final, destrói todas as janelas que ainda possam estar abertas
    cv2.destroyAllWindows()
    print("Servidor encerrado.")
