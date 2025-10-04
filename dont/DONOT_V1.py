import psutil
import ctypes
import time

# --- การตั้งค่าสำหรับการปิดโปรแกรม ---
# รายชื่อกระบวนการ (process names) ที่ต้องการ "ยกเว้น" ไม่ให้ปิด
# ควรเพิ่มโปรแกรมที่จำเป็นต่อการทำงานของระบบ (เช่น explorer.exe) และตัวสคริปต์เอง (เช่น python.exe)
# (ชื่อไฟล์ .exe ต้องตรงกับที่แสดงใน Task Manager)
EXCEPTIONS = ["explorer.exe", "python.exe", "py.exe", "cmd.exe", "powershell.exe", "svchost.exe", "SystemSettings.exe"]

def terminate_all_applications():
    """ตรวจสอบและปิดโปรแกรมที่กำลังทำงานอยู่ทั้งหมด ยกเว้นรายการที่กำหนด"""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # ตรวจสอบว่าชื่อโปรแกรมอยู่ในรายการยกเว้นหรือไม่ โดยไม่คำนึงถึงตัวพิมพ์เล็ก/ใหญ่
            if proc.info['name'].lower() not in [e.lower() for e in EXCEPTIONS]:
                print(f"กำลังปิดโปรแกรม: {proc.info['name']} (PID: {proc.info['pid']})")
                proc.terminate() # ลองสั่งให้ปิดอย่างนุ่มนวลก่อน
                time.sleep(0.1)
                if proc.is_running():
                    proc.kill() # ถ้ายังไม่ปิด ให้สั่งปิดแบบบังคับ
                print(f"ปิดโปรแกรม {proc.info['name']} เรียบร้อย")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass # จัดการข้อผิดพลาดที่อาจเกิดขึ้นระหว่างการเข้าถึงหรือปิดกระบวนการ
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการปิด {proc.info['name']}: {e}")

# --- การตั้งค่าสำหรับการลด DPI เมาส์ (Pointer Speed) ---
# ใน Windows การตั้งค่า DPI เมาส์ในระดับระบบปฏิบัติการคือการตั้งค่า Mouse Pointer Speed
# ค่านี้มีตั้งแต่ 1 (ช้าที่สุด) ถึง 20 (เร็วที่สุด), ค่า 10 คือค่าเริ่มต้น
# ค่าที่ตั้งจะเป็นค่า 1 เพื่อให้ช้าที่สุด ซึ่งเทียบเท่ากับการลด DPI
# SPI_SETMOUSESPEED = 113 (รหัสสำหรับตั้งค่าความเร็วเมาส์)
# SPIF_UPDATEINIFILE = 1
# SPIF_SENDCHANGE = 2
SPI_SETMOUSESPEED = 0x0071
SPIF_SENDCHANGE = 0x0002
MIN_MOUSE_SPEED = 1 # 1 คือค่าที่ช้าที่สุด (ต่ำที่สุด)

def set_mouse_dpi(speed=MIN_MOUSE_SPEED):
    """ตั้งค่า Mouse Pointer Speed ใน Windows ผ่าน ctypes"""
    # SystemParametersInfoA ใช้ในการตั้งค่าพารามิเตอร์ระบบ
    # 1. Action: SPI_SETMOUSESPEED (113)
    # 2. Param1: 0 (ไม่ใช้)
    # 3. Param2: speed (ค่าความเร็วเมาส์ 1-20)
    # 4. Param3: SPIF_SENDCHANGE (แจ้งให้ระบบอื่นๆ ทราบถึงการเปลี่ยนแปลง)
    try:
        ctypes.windll.user32.SystemParametersInfoA(SPI_SETMOUSESPEED, 0, speed, SPIF_SENDCHANGE)
        print(f"ตั้งค่าความเร็วเมาส์เป็น {speed} (DPI ต่ำสุด) เรียบร้อย")
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการตั้งค่าความเร็วเมาส์: {e}")

# --- โปรแกรมหลัก ---
if __name__ == "__main__":
    print("--- โปรแกรมควบคุมเริ่มต้นทำงาน ---")
    set_mouse_dpi(MIN_MOUSE_SPEED) # ตั้งค่า DPI เมาส์ก่อน
    
    while True:
        terminate_all_applications()
        # หน่วงเวลา 1 วินาที ก่อนตรวจสอบซ้ำ เพื่อลดการใช้ CPU
        time.sleep(1)