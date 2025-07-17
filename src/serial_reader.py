import serial
import time
import sys

ENQ = b'\x05'
ACK = b'\x06'
EOT = b'\x04'

CMD_ROTATION_SPEED = b'N'
CMD_HEART_RATE = b'H'

AEROBIKE_ACK_ENABLED = True

def send_command_and_get_data(ser, command, expected_data_len, command_name):
    try:
        ser.flushInput()
        ser.write(command)
        initial_response = ser.read(1)

        if initial_response == ACK:
            if AEROBIKE_ACK_ENABLED:
                ser.write(ACK)
                time.sleep(0.05)
            actual_data = ser.read(expected_data_len)
            if AEROBIKE_ACK_ENABLED and actual_data and actual_data != b'':
                ser.write(ACK)
            return actual_data
        elif initial_response:
            if expected_data_len > 0:
                remaining_data = ser.read(expected_data_len - len(initial_response))
                full_data = initial_response + remaining_data
                if AEROBIKE_ACK_ENABLED and full_data and full_data != b'':
                    ser.write(ACK)
                return full_data
            else:
                return initial_response
        else:
            return b''
    except Exception as e:
        sys.stderr.write(f"Serial error in send_command_and_get_data: {e}\n")
        return None

def parse_data(data_bytes, expected_len=None):
    if not data_bytes:
        return None
    try:
        s_data = data_bytes.decode('ascii')
        if not s_data.isdigit():
            return None
        if expected_len is not None and len(s_data) != expected_len:
            return None
        return int(s_data[::-1])
    except Exception:
        return None

def read_data(ser):
    # 回転数
    rotation_speed_bytes = send_command_and_get_data(ser, CMD_ROTATION_SPEED, 3, "Rotation Speed")
    rotation_speed = parse_data(rotation_speed_bytes, expected_len=3) if rotation_speed_bytes else None

    # 心拍
    heart_rate_bytes = send_command_and_get_data(ser, CMD_HEART_RATE, 3, "Heart Rate")
    heart_rate = parse_data(heart_rate_bytes, expected_len=3) if heart_rate_bytes else None

    return heart_rate, rotation_speed

def set_load(ser, watt):
    """
    負荷（ワット数）を設定する
    watt: int, 0～999
    """
    if not (10 <= watt <= 400):
        raise ValueError("watt must be 10-400")
    watt_str = f"{watt:03d}"[::-1]  # 逆順
    cmd = b'L' + watt_str.encode('ascii')
    print(f"cmd: {cmd}")
    print(f"[set_load] Sending command: {cmd} (ascii: {cmd.decode('ascii')}) for {watt}W")
    ser.flushInput()
    ser.write(cmd)
    time.sleep(0.1)  # ← 追加
    for i in range(5):  # 最大5回リトライ
        ack = ser.read(1)
        print(f"[set_load] Try {i+1}: Received response: {ack} (hex: {ack.hex() if ack else ''})")
        if ack == ACK:
            print("[set_load] ACK received. Load set successfully.")
            return True
        time.sleep(0.1)
    print(f"[set_load] Unexpected response: {ack} (hex: {ack.hex() if ack else ''})")
    return False