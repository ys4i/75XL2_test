import serial
import time
import matplotlib.pyplot as plt
from serial_reader import read_data, set_load

ENQ = b'\x05'
ACK = b'\x06'
EOT = b'\x04'   

def main():
    SERIAL_PORT = '/dev/ttyUSB0'
    BAUD_RATE = 9600
    TIMEOUT = 3

    plt.ion()
    fig, ax = plt.subplots()
    ax.set_title("Real-Time Heart Rate and Rotation Speed")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Values")
    heart_rate_line, = ax.plot([], [], label='Heart Rate (bpm)', color='r')
    rotation_speed_line, = ax.plot([], [], label='Rotation Speed (rpm)', color='b')
    ax.legend()
    
    times = []
    heart_rates = []
    rotation_speeds = []

    ser = None
    try:
        print(f"--- KONAMI AEROBIKE 75XLIII Real-time Monitor (Matplotlib) ---")
        print(f"Attempting to open serial port: {SERIAL_PORT}")
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=TIMEOUT
        )
        print(f"Serial port {SERIAL_PORT} opened successfully.")

        print("Sending ENQ to connect...")
        ser.flushInput()
        ser.write(ENQ)
        response_enq = ser.read(1)

        if response_enq == ACK:
            print("Connection established (received ACK). Sending ACK back...")
            ser.write(ACK)
            time.sleep(0.5)  # 0.5秒～1秒にしてみる
            if set_load(ser, 100):
                print("Load set to 100W.")
            else:
                print("Failed to set load.")
        else:
            print(f"Failed to establish connection. Expected ACK, got: {response_enq} (hex: {response_enq.hex()})")
            print("Please ensure the aerobike is in online mode (START/STOP key + Power ON).")
            print("Also, check your SERIAL_PORT setting.")
            input("\nPress Enter to exit...")
            return

        print("\n--- READY FOR DATA ACQUISITION ---")
        print("*** IMPORTANT: Please ensure the aerobike is in ONLINE mode and start pedaling NOW! ***")
        print("*** Also ensure a heart rate sensor is connected and active if testing heart rate. ***")
        print("\nPress Ctrl+C to stop the monitor.")
        time.sleep(2)

        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time
            heart_rate, rotation_speed = read_data(ser)

            # コマンドラインに表示
            print(f"Time: {elapsed_time:.1f}s | Heart Rate: {heart_rate} bpm | Rotation Speed: {rotation_speed} rpm", end='\r')

            if heart_rate is not None:
                heart_rates.append(heart_rate)
                times.append(elapsed_time)

            if rotation_speed is not None:
                rotation_speeds.append(rotation_speed)

            heart_rate_line.set_data(times, heart_rates)
            rotation_speed_line.set_data(times, rotation_speeds)

            ax.relim()
            ax.autoscale_view()
            plt.pause(0.1)

    except KeyboardInterrupt:
        print("\n--- Stopping data acquisition. ---")
    except Exception as e:
        import sys
        sys.stderr.write(f"\nAn unexpected error occurred: {e}\n")
    finally:
        if ser and ser.is_open:
            print("Sending EOT to disconnect...")
            ser.flushInput()
            ser.write(EOT)
            response_eot = ser.read(1)
            if response_eot == EOT:
                print("Disconnected (received EOT).")
            elif response_eot == ACK: 
                print(f"Disconnected (received ACK {response_eot.hex()} instead of EOT).")
            else:
                print(f"Did not receive EOT response. Expected EOT, got: {response_eot} (hex: {response_eot.hex()})")
            ser.close()
            print("Serial port closed.")
        print("Monitor stopped. Press Enter to close terminal...")
        input()

if __name__ == "__main__":
    main()