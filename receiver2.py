import cv2
import socket
import numpy as np
import struct
from ultralytics import YOLO  # Requer 'pip install ultralytics'

# Parâmetros da conexão
IP_JETSON = '0.0.0.0'
PORT = 8000

# Carrega o modelo YOLOv5/8
model = YOLO('yolov8n.pt')  # ou 'yolov5s.pt' se estiver usando outra versão

# Cria socket TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP_JETSON, PORT))
server_socket.listen(1)

print(f"Aguardando conexão na porta {PORT}...")
conn, addr = server_socket.accept()
print(f"Conectado por {addr}")

data_buffer = b''
payload_size = struct.calcsize(">L")

try:
    while True:
        while len(data_buffer) < payload_size:
            data = conn.recv(4096)
            if not data:
                raise ConnectionError("Cliente desconectado.")
            data_buffer += data

        packed_size = data_buffer[:payload_size]
        data_buffer = data_buffer[payload_size:]
        frame_size = struct.unpack(">L", packed_size)[0]

        while len(data_buffer) < frame_size:
            data = conn.recv(4096)
            if not data:
                raise ConnectionError("Cliente desconectado.")
            data_buffer += data

        frame_data = data_buffer[:frame_size]
        data_buffer = data_buffer[frame_size:]

        np_arr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            print("Frame inválido recebido.")
            continue

        # Aplica detecção com YOLOv
        results = model(frame, verbose=False)[0]
        annotated_frame = results.plot()  # Desenha caixas e rótulos

        cv2.imshow('Jetson - YOLOv Processando', annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    conn.close()
    server_socket.close()
    cv2.destroyAllWindows()
    print("Conexão encerrada.")
