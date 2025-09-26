import socket
import struct
import pickle
import cv2
import numpy as np

def start_client(host, port=9999):
    """
    เชื่อมต่อไปยัง Server และรับภาพมาแสดงผล
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((host, port))
        print(f"[*] Connected to server at {host}:{port}")
    except ConnectionRefusedError:
        print(f"[!] Connection failed. Is the server running at {host}:{port}?")
        return

    data = b""
    # ขนาดของข้อมูล 'L' (unsigned long) คือ 4 bytes
    payload_size = struct.calcsize("L")

    try:
        while True:
            # 1. รับข้อมูลขนาดของ Frame ที่กำลังจะมา
            while len(data) < payload_size:
                data += client_socket.recv(4096) # รับข้อมูลทีละ 4KB
            
            # แยกข้อมูลขนาดของ Frame ออกมา
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("L", packed_msg_size)[0]

            # 2. รับข้อมูล Frame จริงๆ จนกว่าจะครบตามขนาดที่ระบุ
            while len(data) < msg_size:
                data += client_socket.recv(4096)
            
            # แยกข้อมูล Frame ออกมา
            frame_data = data[:msg_size]
            data = data[msg_size:]

            # 3. แปลงข้อมูล Bytes กลับเป็นภาพ (NumPy array)
            frame = pickle.loads(frame_data)

            # 4. แสดงผลภาพด้วย OpenCV
            cv2.imshow('Screen Sharing', frame)
            
            # กด 'q' เพื่อออกจากโปรแกรม
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except Exception as e:
        print(f"[!] An error occurred: {e}")
    finally:
        client_socket.close()
        cv2.destroyAllWindows()
        print("[*] Connection closed.")


if __name__ == "__main__":
    # --- ใส่ IP Address ของเครื่อง Server ตรงนี้ ---
    server_ip = input("Enter Server IP Address: ")
    if not server_ip:
        print("IP Address cannot be empty.")
    else:
        start_client(server_ip)
