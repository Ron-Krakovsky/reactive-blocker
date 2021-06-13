import random
import tkinter as tk
import matplotlib
import serial,time
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from tkinter import ttk  # like css
from matplotlib.animation import FuncAnimation
from matplotlib import style
from bitarray import bitarray

# ------------------------serial description------------------------
ser = serial.Serial()
# ser.port = "/dev/ttyUSB0"
ser.port = 'COM5'
# ser.port = "/dev/ttyS2"
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS  # number of bits per bytes
ser.parity = serial.PARITY_NONE  # set parity check: no parity
ser.stopbits = serial.STOPBITS_TWO  # number of stop bits
# ser.timeout = None          #block read
ser.timeout = 0.2 # non-block read
# ser.timeout = 2              #timeout block read
ser.xonxoff = False  # disable software flow control
ser.rtscts = False  # disable hardware (RTS/CTS) flow control
ser.dsrdtr = False  # disable hardware (DSR/DTR) flow control
ser.writeTimeout = 2

# ------------------------data about fft------------------------
resolution = 195000
frequency = 100000000
Samples = 512
global index_power
# ------------------------gui------------------------
LARGE_FONT=("Verdana", 12)
style.use("ggplot")
f = Figure(figsize=(10, 5), dpi=100)
a = f.add_subplot(111)

# ------------------------main def : gui, serial and more------------------------


def animate(i):

    x_vals = []  # axis x in the graph
    y_vals = []  # axis y in the graph

    try:  # try open serial port
        ser.open()
    except Exception as e:
        print("error open serial port: " + str(e))

    if ser.isOpen():
        inputc.config(text="The device connected ")
        try:
            ser.flushInput()  # clean input data
            ser.flushOutput()  # clean output data

            # write data to fpga
            x = bytes(b'\x0F')
            ser.write(x)
            print("write data : x0F => reset ram for new fft and army data")

            time.sleep(0.1)

            # write data to fpga
            x = bytes(b'\x01')
            ser.write(x)
            print("write data : x01 => Request for FFT")
            response0 = ser.readline(128)  # read data from fpga, max bytes 128
            print(response0)

            ser.flushInput()  # clean input data

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

            r = 0

            #  --------- creating the graph FFT - spectrum analyzer --------
            for counter in range(512):

                # bit_reversed_counter--------------------------------------
                # --- convert from int to byte
                if counter > 0:
                    xaxis_fft = bitarray(bitfield(counter - 1))
                else:
                    xaxis_fft = bitarray(bitfield(counter))

                count = 9 - len(xaxis_fft)  # count indicate how many bits are missing to complete 9 bits number

                for j in range(9 - len(xaxis_fft)):  # add missing bits
                    xaxis_fft.append(False)

                # shift right the bits, for original number
                if count != 0:
                    bitnumber2 = (bitarray('0') * count) + xaxis_fft[:-count]
                else:
                    bitnumber2 = xaxis_fft

                # bit reversed
                y = bitarray('000000000')
                for i in range(9):
                    y[8 - i] = bitnumber2[i]
                xaxis_fft_counter = int(y.to01(), 2)  # convert from byte to int
                # ------------------------------------------------------------

                # organize the axis x, positive x and negative x -------------
                if xaxis_fft_counter < 256:
                    xaxis_fft_counter = xaxis_fft_counter
                else:
                    xaxis_fft_counter = -1 * (512 - xaxis_fft_counter)
                # ------------------------------------------------------------

                # plot on the graph-------------------------------------------
                x_vals.append(xaxis_fft_counter)
                y_vals.append(0)

                x_vals.append(xaxis_fft_counter)
                if counter >= 0 and counter < 128:
                    r = response0[counter]
                elif counter >= 128 and counter < 256:
                    r = response1[counter-128]
                elif counter >= 256 and counter < 384:
                    r = response2[counter-256]
                else:
                    r = response3[counter-384]

                y_vals.append(r)

                x_vals.append(xaxis_fft_counter)
                y_vals.append(0)
                # ------------------------------------------------------------

            a.clear()
            a.plot(x_vals, y_vals, "#00A3E0")  # plot the axis x and axis y on  the graph

            ser.flushInput()

            x = bytes(b'\x05')
            ser.write(x)
            print("write data : x05 => Request for army data")
            response4 = ser.readline(1)
            print("read data (army data) :", response4[0])

            if response4[len(response4) - 1] == 15:
                box.config(bg="green")
                label2.config(text="signal check : ARMY")
            else:
                box.config(bg="red")
                label2.config(text="signal check : ENEMY")

            ser.flushInput()

            x = bytes(b'\x06')
            ser.write(x)
            print("write data : x06 => Request for counter_freq data")
            response5 = ser.readline(1)
            print("read data (army data) :", response5[0])

            a.set_title("FFT (RF signal)\nfrequency RF:" + str(response5[0]*(frequency/Samples)) + "Hz")
            a.set_xlabel('Samples FFT')
            a.set_ylabel('Power FFT')

            ser.close()

        except Exception as e1:
            print("error communicating...: " + str(e1))

    else:
        inputc.config(text= "The device is not connected ")
        print("cannot open serial port ")


def run():
    try:
        ser.open()
    except Exception as e:
        print("error open serial port: " + str(e))

    if ser.isOpen():

        try:
            ser.flushInput()
            ser.flushOutput()

            x = bytes(b'\xF2')
            ser.write(x)
            print("write data : xF2 => Request for FFT")

            ser.close()

        except Exception as e1:
            print("error communicating...: " + str(e1))

    else:
        print("cannot open serial port ")


def Stop():
    try:
        ser.open()
    except Exception as e:
        print("error open serial port: " + str(e))

    if ser.isOpen():

        try:
            ser.flushInput()
            ser.flushOutput()

            x = bytes(b'\xF0')
            ser.write(x)
            print("write data : xF0 => Request for FFT")

            ser.close()

        except Exception as e1:
            print("error communicating...: " + str(e1))

    else:
        print("cannot open serial port ")


def bitfield(n):
    return [int(digit) for digit in bin(n)[2:]]  # convert int to bit array.


class ReactiveBlocker(tk.Tk):  # child class: Tk = Parents class name in package tk.

    def __init__(self, *args, **kwargs):  # individual init fun for this class.

        tk.Tk.__init__(self, *args, **kwargs)  # keep the inheritance of the parent's init function.

        # definition of window -----------------------------------
        tk.Tk.iconbitmap(self, default="logohatal.ico")
        tk.Tk.wm_title(self, "Reactive Blocker (Ron Krakovsky)")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0 , weight=1)
        container.grid_columnconfigure(0 , weight=1)
        # --------------------------------------------------------

        self.frames = {}  # create empty dictionaries for all frames in program.

        # add all frames to dictionaries --------------------------
        for F in (StartPage, MainPage):  # for loop that use names of classes
            frame = F(container, self)  # create object frame from each class and send data about the window
            self.frames[F] = frame  # add to dictionaries the frame
            frame.grid(row=0, column=0, sticky="nsew")
        # ---------------------------------------------------------

        self.show_frame(StartPage)  # call to fun "show frame" and send name of frame.

    def show_frame(self, cont):  # fun that activate the frame according to name frame that received.

        frame = self.frames[cont]  # call from the dictionaries the frame.
        frame.tkraise()  # activate the frame.


class StartPage(tk.Frame):  # child class: Frame = Parents class name in package tk.

    def __init__(self, parent, controller):  # individual init fun for this class.
        tk.Frame.__init__(self, parent)  # keep the inheritance of the parent's init function.

        label = tk.Label(self, text="Reactive Blocker", font=LARGE_FONT)  # object - Text.
        label.pack(pady=10, padx=10)  # pack this object on screen and give direction.

        button1 = ttk.Button(self, text="Start Program", command=lambda: controller.show_frame(MainPage))  # object - button.
        button1.pack(pady=10)

        text_d = tk.Label(self, text="Name : Ron Krakovsky\nLast Update : 09/06/2021\n", font=LARGE_FONT)  # object - Text.
        text_d.pack(pady=10, padx=10)

        global inputc
        inputc = tk.Label(self, text="", font=LARGE_FONT)  # object - Text.
        inputc.pack(pady=100, padx=10)  # pack this object on screen


class MainPage(tk.Frame):  # child class: Frame = Parents class name in package tk.

    def __init__(self, parent, controller):  # individual init fun for this class.
        tk.Frame.__init__(self, parent)  # keep the inheritance of the parent's init function.

        label = tk.Label(self, text="Reactive Blocker", font=LARGE_FONT)  # object - Text.
        label.pack(pady=10, padx=10)  # pack this object on screen and give direction.

        # show graph on screen ----------------------
        canvas = FigureCanvasTkAgg(f, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # -------------------------------------------

        # tool bar for graph ------------------------
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # -------------------------------------------

        button1 = ttk.Button(self, text="Back", command=lambda: controller.show_frame(StartPage))  # object - button.
        button1.place(x=3, y=3)  # pack this object on screen and give direction.

        button2 = ttk.Button(self, text="Run", command=run)  # object - button.
        button2.place(x=80, y=3)

        button3 = ttk.Button(self, text="Stop", command=Stop)  # object - button.
        button3.place(x=157, y=3)

        global box
        box = tk.Frame(self, width=20, height=20, bg="red")  # object - Box frame.
        box.pack(side=tk.LEFT, pady=2, padx=10)

        global label2
        label2 = tk.Label(self, text="signal check : ENEMY", font=LARGE_FONT)  # object - Text.
        label2.pack(side=tk.LEFT, pady=20)

        a.set_xlabel('Samples FFT')
        a.set_ylabel('Power FFT')
        a.set_title("FFT (RF signal)\nfrequency RF: 0 Hz")


app = ReactiveBlocker()  # call to main class
ani = FuncAnimation(f, animate, interval=10)  # call func animation class and send name def of animate in my program.
app.mainloop()
