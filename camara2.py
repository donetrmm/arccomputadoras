import serial
import tkinter as tk
import cv2
from PIL import Image, ImageTk

try:
    ser = serial.Serial('/dev/ttyACM0', 9600)
except serial.SerialException:
    print("No se pudo abrir el puerto serial.")
    exit()

distancias = []

def read_serial():
    if ser.in_waiting > 0:
        try:
            line = ser.readline().decode('utf-8').rstrip()
            leds_on = int(line)
            line = ser.readline().decode('utf-8').rstrip() 
            distance = int(line)
            update_gui(leds_on, distance)
            print(f'LEDs encendidos: {leds_on}, Distancia: {distance}')
            distancias.append(distance)
            if len(distancias) > 12:
                distancias.pop(0)
        except ValueError:
            pass
        except serial.SerialException:
            print("Error de lectura del puerto serial.")
    root.after(100, read_serial)

def update_gui(leds_on, distance):
    label_var.set(f'LEDs encendidos: {leds_on}')
    update_led_colors(leds_on)
    distancia.config(text=f"Distancia: {distance}")
    last_distances = distancias[-12:]
    last_distances_str = '\n'.join(str(dist) for dist in last_distances)
    distancia_ultimas.delete(1.0, tk.END)
    distancia_ultimas.insert(tk.END, last_distances_str)

def update_led_colors(leds_on):
    leds_labels = [led1, led2, led3, led4, led5]
    for i, label in enumerate(leds_labels):
        if i < leds_on:
            label.config(bg=colors_on[i])
        else:
            label.config(bg=colors_off[i])

def show_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = Image.fromarray(frame)
        frame = ImageTk.PhotoImage(frame)
        video_label.img = frame
        video_label.config(image=frame)
    root.after(10, show_frame)

root = tk.Tk()
root.geometry("1020x720")
root.title("Distancias con Python y Arduino UNO")

colors_on = ["#0CFA38", "#2166FA", "#FA2C33", "#FA2C33", "#FAEF1D"]
colors_off = ["#7FFA96", "#89B5FA", "#FAA9AD", "#FAA9AD", "#FAF39D"]

# Main title
label_var = tk.StringVar()
label = tk.Label(root, textvariable=label_var, font=('Helvetica', 24))
label.pack(pady=20)

# LED Frame
led_frame = tk.Frame(root)
led_frame.pack(pady=20)

led1 = tk.Label(led_frame, width=4, height=2, bg=colors_off[0])
led1.grid(row=0, column=0, padx=10)
led2 = tk.Label(led_frame, width=4, height=2, bg=colors_off[1])
led2.grid(row=0, column=1, padx=10)
led3 = tk.Label(led_frame, width=4, height=2, bg=colors_off[2])
led3.grid(row=0, column=2, padx=10)
led4 = tk.Label(led_frame, width=4, height=2, bg=colors_off[3])
led4.grid(row=0, column=3, padx=10)
led5 = tk.Label(led_frame, width=4, height=2, bg=colors_off[4])
led5.grid(row=0, column=4, padx=10)

# Distance Frame
distance_frame = tk.Frame(root)
distance_frame.pack(pady=20)

distancia = tk.Label(distance_frame, text="Distancia: 0", font=('Helvetica', 16))
distancia.pack()

# Last distances Frame
last_distances_frame = tk.Frame(root)
last_distances_frame.pack(pady=20)

distancia_ultimas = tk.Text(last_distances_frame, height=12, width=20, font=('Helvetica', 12))
distancia_ultimas.pack()

# Camera Frame
cap = cv2.VideoCapture(0)
video_label = tk.Label(root)
video_label.pack()

read_serial()
show_frame()

root.mainloop()
