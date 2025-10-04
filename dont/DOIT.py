import ctypes

# --- การตั้งค่า DPI เมาส์กลับเป็นปกติ ---
# รหัส API และค่าคงที่
SPI_SETMOUSESPEED = 0x0071
SPIF_SENDCHANGE = 0x0002
DEFAULT_MOUSE_SPEED = 10  # ค่าเริ่มต้นของ Windows คือ 10 (จาก 1 ถึง 20)

def reset_mouse_speed(speed=DEFAULT_MOUSE_SPEED):
    """ตั้งค่า Mouse Pointer Speed กลับสู่ค่าปกติ (10) ใน Windows ผ่าน ctypes"""
    try:
        # เรียกใช้ Windows API เพื่อปรับความเร็วเมาส์
        ctypes.windll.user32.SystemParametersInfoA(SPI_SETMOUSESPEED, 0, speed, SPIF_SENDCHANGE)
        print(f"✅ ตั้งค่าความเร็วเมาส์กลับเป็นปกติที่ {speed} เรียบร้อยแล้ว")
        print("โปรดทดสอบการเคลื่อนไหวของเมาส์")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการตั้งค่าความเร็วเมาส์: {e}")

# --- โปรแกรมหลัก ---
if __name__ == "__main__":
    reset_mouse_speed()