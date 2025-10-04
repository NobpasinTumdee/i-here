import psutil
import ctypes
import time

# --- การตั้งค่าสำหรับการลด DPI เมาส์ ---
# SPI_SETMOUSESPEED = 113 (รหัสสำหรับตั้งค่าความเร็วเมาส์)
# SPIF_SENDCHANGE = 2
SPI_SETMOUSESPEED = 0x0071
SPIF_SENDCHANGE = 0x0002
MIN_MOUSE_SPEED = 1 # 1 คือค่าที่ช้าที่สุด (ต่ำที่สุด)

def set_mouse_dpi(speed=MIN_MOUSE_SPEED):
    """ตั้งค่า Mouse Pointer Speed ใน Windows ผ่าน ctypes"""
    try:
        # เรียกใช้ Windows API เพื่อปรับความเร็วเมาส์
        ctypes.windll.user32.SystemParametersInfoA(SPI_SETMOUSESPEED, 0, speed, SPIF_SENDCHANGE)
        print(f"[Mouse] ตั้งค่าความเร็วเมาส์เป็น {speed} (DPI ต่ำสุด) เรียบร้อย")
    except Exception as e:
        print(f"[Mouse] เกิดข้อผิดพลาดในการตั้งค่าความเร็วเมาส์: {e}")

# --- การจัดการโปรแกรม ---
# รายชื่อกระบวนการที่ "ห้ามปิด" เด็ดขาด (ส่วนใหญ่เป็นระบบปฏิบัติการและตัวสคริปต์เอง)
# โปรแกรมเหล่านี้จะถูกยกเว้นแม้ว่าจะเปิดหลังสคริปต์ก็ตาม
SYSTEM_EXCEPTIONS = [
    "explorer.exe", "python.exe", "py.exe", "cmd.exe", "powershell.exe", 
    "conhost.exe", "csrss.exe", "wininit.exe", "lsass.exe", 
    "smss.exe", "winlogon.exe", "SystemSettings.exe", "RuntimeBroker.exe",
    "dwm.exe", "taskhostw.exe", "svchost.exe"
]

def get_running_process_names():
    """ดึงรายชื่อชื่อกระบวนการทั้งหมดที่กำลังทำงานอยู่"""
    names = set()
    for proc in psutil.process_iter(['name']):
        try:
            # เพิ่มชื่อกระบวนการเป็นตัวพิมพ์เล็กเข้าสู่ Set
            names.add(proc.info['name'].lower())
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return names

def terminate_new_applications(initial_processes):
    """ตรวจสอบและปิดโปรแกรมที่เพิ่งเปิดหลังจากสคริปต์เริ่มทำงาน"""
    # ดึงรายชื่อกระบวนการปัจจุบัน
    current_processes = get_running_process_names()
    
    # คำนวณหาโปรแกรมใหม่: คือโปรแกรมในปัจจุบันที่ไม่อยู่ในรายการเริ่มต้น
    new_processes = current_processes - initial_processes

    if new_processes:
        for new_app_name in list(new_processes): # วนลูปในสำเนาของ Set
            # 1. ตรวจสอบว่าโปรแกรมใหม่นี้เป็นโปรแกรมของระบบที่ต้องยกเว้นหรือไม่
            if new_app_name in [e.lower() for e in SYSTEM_EXCEPTIONS]:
                # ถ้าเป็นโปรแกรมของระบบ: ให้เพิ่มเข้าไปในรายการเริ่มต้นเพื่อยกเว้นถาวร
                initial_processes.add(new_app_name)
                print(f"[Monitor] ยกเว้นกระบวนการระบบใหม่: {new_app_name}")
                continue
            
            # 2. ถ้าไม่ใช่โปรแกรมระบบ ให้ทำการปิด
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'].lower() == new_app_name:
                        print(f"[Action] กำลังปิดโปรแกรมใหม่: {proc.info['name']} (PID: {proc.info['pid']})")
                        proc.terminate() # ลองสั่งให้ปิดอย่างนุ่มนวลก่อน
                        time.sleep(0.1)
                        if proc.is_running():
                            proc.kill() # ถ้ายังไม่ปิด ให้สั่งปิดแบบบังคับ
                        
                        # ลบโปรแกรมที่ปิดสำเร็จออกจากรายการโปรแกรมใหม่
                        if not proc.is_running():
                            # เพื่อให้สคริปต์ไม่ต้องพยายามปิดโปรแกรมนี้ซ้ำ ๆ หากมันถูกปิดไปแล้ว
                            new_processes.discard(new_app_name) 
                            print(f"[Success] ปิดโปรแกรม {new_app_name} เรียบร้อย")

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                except Exception as e:
                    print(f"[Error] เกิดข้อผิดพลาดในการปิด {new_app_name}: {e}")
    else:
        # print("[Status] ไม่พบโปรแกรมใหม่ที่ต้องปิด...")
        pass # ปิดบรรทัดนี้เพื่อไม่ให้มีข้อความรบกวนมากเกินไป

# --- โปรแกรมหลัก ---
if __name__ == "__main__":
    
    # 1. ตั้งค่า DPI เมาส์ก่อน
    set_mouse_dpi(MIN_MOUSE_SPEED) 
    
    # 2. บันทึกรายชื่อโปรแกรมที่กำลังทำงานอยู่ ณ จุดเริ่มต้น (Snapshot)
    initial_processes = get_running_process_names()
    print("-" * 50)
    print(f"[Startup] สคริปต์เริ่มต้นทำงาน พร้อมโปรแกรมเริ่มต้น {len(initial_processes)} รายการ")
    print("-" * 50)
    
    # 3. เริ่มวนลูปตรวจสอบ
    try:
        while True:
            terminate_new_applications(initial_processes)
            # หน่วงเวลา 1 วินาที ก่อนตรวจสอบซ้ำ เพื่อลดการใช้ CPU
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n--- สคริปต์ถูกยกเลิกโดยผู้ใช้ ---")
    except Exception as e:
        print(f"\n--- เกิดข้อผิดพลาดร้ายแรง: {e} ---")