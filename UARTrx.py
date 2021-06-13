import serial,time
from bitarray import bitarray


ser = serial.Serial()
# ser.port = "/dev/ttyUSB0"
ser.port = 'COM3'
# ser.port = "/dev/ttyS2"
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
ser.parity = serial.PARITY_NONE  # set parity check: no parity
ser.stopbits = serial.STOPBITS_TWO  # number of stop bits
#ser.timeout = None          #block read
ser.timeout = 0.2 # non-block read
# ser.timeout = 2              #timeout block read
ser.xonxoff = False  # disable software flow control
ser.rtscts = False  # disable hardware (RTS/CTS) flow control
ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
ser.writeTimeout = 2

frequency = 100000000
Samples = 512


def bitfield(n):
    return [int(digit) for digit in bin(n)[2:]]


def Frequency_calculation(num, add):
    max_frequency = 0
    for i in range(128):
        if (num[i] > 100):
            counter_index = i + add
            bit_number = bitarray(bitfield(counter_index))
            y = bitarray('000000000')
            for j in range(9):
                y[8 - j] = bit_number[j]
            bit_reversed = int(y.to01(), 2)
            if bit_reversed < Samples/2:
                freq = bit_reversed*(frequency/Samples)
                if freq > max_frequency:
                    max_frequency = freq

    return (max_frequency)


try:
    ser.open()
except Exception as e:
    print("error open serial port: " + str(e))
    exit()

if ser.isOpen():

    try:
        ser.flushInput()
        ser.flushOutput()

        # write data
        x = bytes(b'\x0F')
        ser.write(x)
        print("write data : x0F => reset ram for new fft and army data")

        time.sleep(0.1)

        x = bytes(b'\x01')
        ser.write(x)
        print("write data : x01 => Request for FFT")
        response0 = ser.readline(128)#max 128
        print(response0)

        ser.flushInput()

        x = bytes(b'\x02')
        ser.write(x)
        print("write data : x02 => Request for FFT")
        response1 = ser.readline(128)  # max 128
        print(response1)

        ser.flushInput()

        x = bytes(b'\x03')
        ser.write(x)
        print("write data : x03 => Request for FFT")
        response2 = ser.readline(128)  # max 128
        print(response2)

        ser.flushInput()

        x = bytes(b'\x04')
        ser.write(x)
        print("write data : x04 => Request for FFT")
        response3 = ser.readline(128)  # max 128
        print(response3)

        ser.flushInput()


        x = bytes(b'\x05')
        ser.write(x)
        print("write data : x05 => Request for army data")
        response4 = ser.readline(1)
        print(len(response4))
        print("read data (army data) :", response4[0])

        ser.flushInput()

        x = bytes(b'\x06')
        ser.write(x)
        print("write data : x06 => Request for counter_freq data")
        response5 = ser.readline(1)
        print("read data (army data) :", response5[0])


        ser.close()

    except Exception as e1:
        print("error communicating...: " + str(e1))

else:
    print("cannot open serial port ")
