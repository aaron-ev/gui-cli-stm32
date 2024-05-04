import serial

# Define the serial port and baud rate
serial_port = 'COM7'
baud_rate = 9600

try:
    # Open the serial port
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print("Serial port opened successfully.")

    # Write data to the serial port
    data_to_send = "\n"
    ser.write(data_to_send.encode())
    print("Data sent to the serial port:", data_to_send)

    # Close the serial port
    ser.close()
    print("Serial port closed.")

except serial.SerialException as e:
    print("Serial port error:", e)

except Exception as e:
    print("Error:", e)
