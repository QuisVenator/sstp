import serial
import binascii
import sys
from tqdm import tqdm
import time

def send_file_via_serial(address, filename, serial_port, baudrate):
    try:
        ser = serial.Serial(serial_port, baudrate)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        sys.exit(1)

    try:
        with open(filename, 'rb') as file:
            data = file.read()
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        ser.close()
        sys.exit(1)

    try:
        address = int(address, 16)
    except ValueError:
        print(f"Invalid address: {address}")
        ser.close()
        sys.exit(1)

    current_byte = data[0]
    repeat_count = 1

    with tqdm(total=len(data), unit='B', unit_scale=True, unit_divisor=1024) as pbar:
        for byte in data[1:]:
            if byte == current_byte:
                repeat_count += 1
            else:
                write_command = f"mw.b {hex(address)} 0x{binascii.hexlify(bytes([current_byte])).decode('utf-8')} {repeat_count}\r\n"
                ser.write(write_command.encode('utf-8'))
                ser.flush()
                time.sleep(0.001)  # 1ms sleep
                address += repeat_count
                repeat_count = 1
                current_byte = byte

            pbar.update(1)

        # Send the last group of repeated bytes
        write_command = f"mw.b {hex(address)} 0x{binascii.hexlify(bytes([current_byte])).decode('utf-8')} {repeat_count}\r\n"
        ser.write(write_command.encode('utf-8'))
        ser.flush()

    ser.close()

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python transfer_file.py <ADDRESS> <FILENAME> <SERIAL_PORT> <BAUDRATE>")
        sys.exit(1)

    address = sys.argv[1]
    filename = sys.argv[2]
    serial_port = sys.argv[3]
    baudrate = int(sys.argv[4])

    send_file_via_serial(address, filename, serial_port, baudrate)
