import socket
import struct
import pickle
import mss
import numpy as np

def start_server(host='0.0.0.0', port=9999):
    """
    เริ่มต้น Server เพื่อรอการเชื่อมต่อและส่งภาพหน้าจอ
    host='0.0.0.0' หมายถึงรอรับการเชื่อมต่อจากทุก IP Address ในเครือข่าย
    """
    # 1. สร้าง Socket และรอการเชื่อมต่อ
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"[*] Server listening on {host}:{port}")

    # รอรับการเชื่อมต่อจาก Client
    client_socket, addr = server_socket.accept()
    print(f"[*] Accepted connection from: {addr}")

    # 2. เริ่มต้นการจับภาพหน้าจอ
    with mss.mss() as sct:
        # กำหนดขนาดจอภาพที่ต้องการจับ (ในที่นี้คือทั้งหน้าจอ)
        monitor = sct.monitors[1] 
        
        try:
            while True:
                # 3. จับภาพหน้าจอ
                screenshot = sct.grab(monitor)
                
                # แปลงภาพเป็น NumPy array เพื่อให้ง่ายต่อการจัดการ
                img = np.array(screenshot)
                
                # 4. แปลงข้อมูลภาพ (Frame) เป็น Bytes
                # pickle.dumps() จะแปลง array ของภาพให้เป็นชุดของ bytes
                frame_data = pickle.dumps(img)
                
                # 5. แพ็คขนาดของข้อมูลภาพแล้วส่งไปก่อน
                # 'L' คือ unsigned long (4 bytes)
                # Client จะได้รู้ว่าต้องรับข้อมูลอีกกี่ bytes ถึงจะครบ 1 ภาพ
                message_size = struct.pack("L", len(frame_data))
                
                # 6. ส่งข้อมูลขนาดของภาพ ตามด้วยข้อมูลภาพจริงๆ
                client_socket.sendall(message_size + frame_data)

        except (socket.error, ConnectionResetError):
            print("[-] Client disconnected.")
        finally:
            # ปิดการเชื่อมต่อเมื่อ Client หลุดไป
            client_socket.close()
            server_socket.close()
            print("[*] Server shut down.")

if __name__ == "__main__":
    # คุณต้องรู้ IP Address ของเครื่องนี้ เพื่อให้ Client เชื่อมต่อเข้ามา
    # สามารถหาได้โดยใช้คำสั่ง ipconfig (Windows) หรือ ifconfig (macOS/Linux)
    my_ip = socket.gethostbyname(socket.gethostname())
    print(f"!!! Your local IP address is: {my_ip} !!!")
    print("Tell the client to connect to this IP.")
    
    start_server()
