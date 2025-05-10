# read_serial.py
import serial

SERIAL_PORT = "/dev/ttyUSB0"  # Adjust based on your hardware (e.g., /dev/ttyS0 or /dev/ttyACM0)
BAUD_RATE = 9600

def get_temperature():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
            line = ser.readline().decode('utf-8').strip()
            if "ERROR" in line or not line:
                return None
            return float(line)
    except Exception as e:
        print("Serial read error:", e)
        return None
