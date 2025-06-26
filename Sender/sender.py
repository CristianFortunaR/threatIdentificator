import cv2
import socket
import numpy as np
import struct
import time
import argparse

IP_JETSON = '191.4.205.100'
PORT = 8000

def connect_to_jetson(ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            print(f"Tentando conectar ao Jetson em {ip}:{port}...")
            client_socket.connect((ip, port))
            print(f"Conectado ao Jetson em {ip}:{port}")
            return client_socket
        except socket.error as e:
            print(f"Erro de conexão: {e}. Verifique o IP/Porta ou se o Receiver está rodando. Tentando novamente em 5 segundos...")
            time.sleep(5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Envia frames da webcam para um dispositivo Jetson.")
    parser.add_argument("--ip", type=str, default=IP_JETSON, help=f"Endereço IP do Jetson (padrão: {IP_JETSON}).")
    parser.add_argument("--port", type=int, default=PORT, help=f"Porta para a conexão com o Jetson (padrão: {PORT}).")
    args = parser.parse_args()

    IP_JETSON = args.ip
    PORT = args.port

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Erro ao abrir a webcam. Verifique se ela está conectada e não está em uso.")
        exit()

    client_socket = None
    try:
        client_socket = connect_to_jetson(IP_JETSON, PORT)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Falha ao ler frame da webcam. Encerrando o streaming.")
                break

            # Codifica o frame em JPEG para compressão antes do envio
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            data = buffer.tobytes()
            size = len(data)

            try:
                # Envia o tamanho dos dados do frame (4 bytes)
                client_socket.sendall(struct.pack(">L", size))
                # Envia os dados do frame
                client_socket.sendall(data)
            except socket.error as e:
                print(f"Erro de envio ({e}). Conexão perdida ou problema de rede. Tentando reconectar...")
                if client_socket:
                    client_socket.close()
                client_socket = connect_to_jetson(IP_JETSON, PORT)
                continue # Continua para a próxima iteração do loop para tentar enviar o próximo frame

            # Exibe o frame localmente no PC
            cv2.imshow('PC - Enviando', frame)

            # Pressione 'q' para sair
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Encerrando o streaming por solicitação do usuário.")
                break

    finally:
        # Garante que os recursos são liberados ao finalizar
        cap.release()
        if client_socket:
            client_socket.close()
            print("Conexão com o Jetson encerrada.")
        cv2.destroyAllWindows()
        print("Recursos liberados.")