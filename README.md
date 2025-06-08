# 🚨 Edge AI for Identifying Real-Time Threats

## 📘 Overview

This project explores the full potential of edge computing using NVIDIA's Jetson AGX Orin to detect real-time threats through deep learning models. By leveraging Edge AI, we eliminate latency, enabling immediate response to critical situations such as intrusions, weapons detection, or dangerous objects.

---

## 🤖 Why Edge AI?

Edge AI brings machine learning inference directly to the device, reducing dependency on cloud infrastructure. This is vital for real-time applications where low latency and high availability are essential, such as:
- Security & Surveillance
- Industrial Safety
- Smart Cities
- Autonomous Navigation

---

## 🧠 Hardware: Jetson AGX Orin

<img width="602" alt="Captura de Tela 2025-06-08 às 17 00 32" src="https://github.com/user-attachments/assets/d568f200-a06d-43c3-9de6-1cb12e625ab3" />

We use the **Jetson AGX Orin**, an AI-ready embedded system built by NVIDIA. Key features:
- 275 TOPS (trillion operations per second)
- ARM architecture
- Ideal for Generative AI and Computer Vision at the edge
- Runs full YOLO models with hardware acceleration

---

## 📡 System Architecture

- The **Sender** captures and sends frames over TCP.
- The **Receiver** (Jetson AGX Orin) performs object detection using YOLOv8.

---

## 📤 Sender Script: `sender.py`

Captures a single frame from the webcam and sends it over the network to the Jetson device.

### 🔧 Dependencies:
```bash
pip install opencv-python
```
### How it works:
Captures image using OpenCV.

Encodes and serializes using pickle.

Sends the image via TCP socket.

### 📁 Project Structure
├── sender.py        # Captures and sends a single image

├── receiver2.py     # Receives image and runs YOLOv8 detection

├── README.md        # You are here!


