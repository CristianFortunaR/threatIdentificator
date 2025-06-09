import cv2
import socket
import numpy as np
import struct

IP_JETSON = '191.4.205.100'
PORT = 8000

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erro ao abrir a webcam.")
    exit()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP_JETSON, PORT))
print(f"Conectado ao Jetson em {IP_JETSON}:{PORT}")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        data = buffer.tobytes()
        size = len(data)

        # envia o tamanho como 4 bytes
        client_socket.sendall(struct.pack(">L", size))
        client_socket.sendall(data)

        cv2.imshow('PC - Enviando', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    client_socket.close()
    cv2.destroyAllWindows()
