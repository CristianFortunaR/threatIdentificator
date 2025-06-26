## 📤 Sender Script: `sender.py`

Este script é responsável por capturar o feed de vídeo de uma webcam local e transmiti-lo via rede (TCP) para o dispositivo Jetson AGX Orin.

### 💡 Por que este Sender Aprimorado?

Esta versão do `sender.py` foi desenvolvida para ser mais robusta e flexível, garantindo:
* **Streaming em Tempo Real:** Captura e envia frames contínuos da webcam.
* **Confiabilidade:** Inclui tratamento de erros de conexão e reconexão automática em caso de interrupções na rede ou no receptor.
* **Flexibilidade:** Permite configurar o endereço IP e a porta do dispositivo receptor via linha de comando.
* **Eficiência:** Comprime os frames em JPEG antes do envio para otimizar o uso da largura de banda.

### ⚙️ Como Funciona?

O `sender.py` opera da seguinte forma:
1.  **Inicialização da Câmera:** Acessa a webcam padrão do sistema (`cv2.VideoCapture(0)`).
2.  **Conexão TCP Robusta:** Tenta estabelecer uma conexão TCP com o endereço IP e porta especificados (padrão ou via argumento). Em caso de falha inicial ou perda de conexão durante o streaming, ele tenta reconectar automaticamente a cada 5 segundos.
3.  **Loop de Streaming:** Em um loop contínuo:
    * Lê um frame da webcam.
    * Codifica o frame lido para o formato JPEG, reduzindo o tamanho dos dados para transmissão eficiente. A qualidade da compressão é definida em 80%.
    * Empacota o tamanho dos dados do frame (em bytes) e o envia primeiro através do socket. Isso permite que o receptor saiba exatamente quantos dados esperar para o frame subsequente.
    * Envia os dados binários do frame JPEG pela rede.
    * Exibe o frame sendo enviado em uma janela local (`cv2.imshow`) para monitoramento.
4.  **Encerramento:** O streaming pode ser interrompido a qualquer momento pressionando a tecla 'q' na janela de exibição. O script garante que a câmera seja liberada e a conexão de rede seja fechada de forma limpa.

### Como Executar o sender?
Para Iniciar o streaming da cam, nesse caso uma webcam(0)

```bash
python sender.py [OPÇÕES]
```
**Opções** 
```bash
--ip <endereço IP>
```
Opicional pois define um endereço de IP por Padrão ja temos um endereço no codigo

```bash
--port <numero da porta>
```
Opicional, defina uma porta de comunicação TCP, no codigo o padrão é `8000`

**Exemplos**
Usando porta e IP padrão
```bash
python sender.py
```

Especificando Porta e IP diferentes
```bash 
python sender.py --ip 192.168.1.100 --port 7000
```
**Interrompendo o Script**
basta precionar a tecla `q` enquanto a janela `PC - Enviando` estiver aberta.

### 🔧 Dependências:
```bash
pip install opencv-python numpy