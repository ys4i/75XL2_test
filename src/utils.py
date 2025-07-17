def parse_heart_rate(data_bytes):
    if not data_bytes:
        return None
    try:
        s_data = data_bytes.decode('ascii')
        if s_data.isdigit():
            return int(s_data[::-1])
        else:
            return None
    except (ValueError, UnicodeDecodeError):
        return None

def parse_rotation_speed(data_bytes):
    if not data_bytes:
        return None
    try:
        s_data = data_bytes.decode('ascii')
        if s_data.isdigit():
            return int(s_data[::-1])
        else:
            return None
    except (ValueError, UnicodeDecodeError):
        return None

def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"