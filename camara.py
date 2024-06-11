import serial
import tkinter as tk
import threading
import cv2

# Configuración del puerto serial
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
    distancia_ultimas.delete(1.0, tk.END)  # Limpiar el contenido anterior
    distancia_ultimas.insert(tk.END, last_distances_str)

def update_led_colors(leds_on):
    leds_labels = [led1, led2, led3, led4, led5]
    for i, label in enumerate(leds_labels):
        if i < leds_on:
            label.config(bg=colors_on[i])
        else:
            label.config(bg=colors_off[i])

def video_loop():
    cam_normal = cv2.VideoCapture(0)
    cam_infrared = cv2.VideoCapture(1)

    if not cam_normal.isOpened() or not cam_infrared.isOpened():
        print("Error: No se pudo abrir una o ambas cámaras.")
        return

    while True:
        ret_normal, frame_normal = cam_normal.read()
        ret_infrared, frame_infrared = cam_infrared.read()

        if not ret_normal or not ret_infrared:
            print("Error: No se pudo leer un frame de una o ambas cámaras.")
            break

        cv2.imshow('Camara Normal', frame_normal)
        cv2.imshow('Camara Infrarroja', frame_infrared)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam_normal.release()
    cam_infrared.release()
    cv2.destroyAllWindows()

# Configuración de la ventana principal de Tkinter
root = tk.Tk()
root.geometry("1020x720")
root.title("Distancias con Python y Arduino UNO")

colors_on = ["#0CFA38", "#2166FA", "#FA2C33", "#FA2C33", "#FAEF1D"]
colors_off = ["#7FFA96", "#89B5FA", "#FAA9AD", "#FAA9AD", "#FAF39D"]

label_var = tk.StringVar()
label = tk.Label(root, textvariable=label_var, font=('Helvetica', 24))
label.pack(pady=20)

led1 = tk.Label(root, width=4, height=2, bg=colors_off[0])
led1.place(x=30, y=30)
led2 = tk.Label(root, width=4, height=2, bg=colors_off[1])
led2.place(x=90, y=30)
led3 = tk.Label(root, width=4, height=2, bg=colors_off[2])
led3.place(x=150, y=30)
led4 = tk.Label(root, width=4, height=2, bg=colors_off[3])
led4.place(x=210, y=30)
led5 = tk.Label(root, width=4, height=2, bg=colors_off[4])
led5.place(x=270, y=30)

distancia = tk.Label(root, text="Distancia: 0")
distancia.place(x=480, y=100)

distancia_ultimas = tk.Text(root, height=12, width=20)
distancia_ultimas.place(x=480, y=150)

# Iniciar la lectura del puerto serial
read_serial()

# Crear e iniciar un thread para el bucle de video
video_thread = threading.Thread(target=video_loop)
video_thread.daemon = True
video_thread.start()

# Iniciar el loop principal de Tkinter
root.mainloop()
