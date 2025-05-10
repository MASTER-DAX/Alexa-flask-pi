# read_serial.py
import serial

SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600

def get_temperature():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
            line = ser.readline().decode('utf-8').strip()
            if "ERROR" in line:
                return None
            return float(line)
    except Exception:
        return None
