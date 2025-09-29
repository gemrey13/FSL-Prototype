import tkinter as tk
from tkinter import Label, Button, Scale, OptionMenu, StringVar, IntVar
import cv2
from ultralytics import YOLO
from PIL import Image, ImageTk
import threading

video_label = None
running = False
model = None
cap = None

def on_enter(e):
    e.widget["background"] = BTN_HOVER.get()

def on_leave(e):
    e.widget["background"] = BTN_COLOR.get()

def styled_button(master, text, command):
    btn = Button(
        master,
        text=text,
        command=command,
        font=("Arial", 14, "bold"),
        bg=BTN_COLOR.get(),
        fg=TEXT_COLOR.get(),
        activeforeground=TEXT_COLOR.get(),
        activebackground=BTN_HOVER.get(),
        relief="flat",
        width=20,
        height=2
    )
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn

def start_detection():
    global video_label, running, cap
    running = True

    if cap:
        cap.release()
    cap = cv2.VideoCapture(0)
    cap.set(3, cam_width.get())
    cap.set(4, cam_height.get())

    for widget in window.winfo_children():
        widget.destroy()

    video_label = Label(window, bg=BG_COLOR.get())
    video_label.pack(pady=20)

    back_button = styled_button(window, "Back to Menu", show_menu)
    back_button.pack(pady=15)

    update_frame()

def update_frame():
    global running
    if not running:
        return

    ret, frame = cap.read()
    if not ret:
        return

    frame = cv2.flip(frame, 1)

    results = model.predict(frame, imgsz=416, conf=0.5, verbose=False)
    annotated_frame = results[0].plot()

    img = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=img)

    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    window.after(10, update_frame)

def show_about():
    for widget in window.winfo_children():
        widget.destroy()

    title = Label(window, text="About This Project", font=("Arial", 26, "bold"), bg=BG_COLOR.get(), fg=TEXT_COLOR.get())
    title.pack(pady=30)

    info = (
        "This application uses a YOLO model for hand sign detection.\n"
        "The model was trained on a dataset of more than 13,000 images.\n"
        "It is designed to recognize hand signs in real time using your webcam.\n\n"
        "Performance may vary depending on your device specifications.\n"
        "This project is still in prototype stage."
    )

    label_info = Label(window, text=info, font=("Arial", 14), bg=BG_COLOR.get(), fg=NOTE_COLOR.get(), justify="center", wraplength=700)
    label_info.pack(pady=20)

    back_button = styled_button(window, "Back to Menu", show_menu)
    back_button.pack(pady=20)

def show_settings():
    for widget in window.winfo_children():
        widget.destroy()

    title = Label(window, text="Settings", font=("Arial", 26, "bold"), bg=BG_COLOR.get(), fg=TEXT_COLOR.get())
    title.pack(pady=30)

    # Camera size
    res_label = Label(window, text="Camera Resolution", font=("Arial", 14), bg=BG_COLOR.get(), fg=NOTE_COLOR.get())
    res_label.pack(pady=5)
    res_menu = OptionMenu(window, cam_width, 320, 640, 800, 1280)
    res_menu.config(bg=BTN_COLOR.get(), fg=TEXT_COLOR.get(), font=("Arial", 12))
    res_menu.pack(pady=5)
    res_menu_h = OptionMenu(window, cam_height, 240, 480, 600, 720)
    res_menu_h.config(bg=BTN_COLOR.get(), fg=TEXT_COLOR.get(), font=("Arial", 12))
    res_menu_h.pack(pady=5)

    # Background color
    bg_label = Label(window, text="Background Color", font=("Arial", 14), bg=BG_COLOR.get(), fg=NOTE_COLOR.get())
    bg_label.pack(pady=5)
    bg_menu = OptionMenu(window, BG_COLOR, "#1e1e2f", "#ffffff", "#000000", "#2f4f4f")
    bg_menu.config(bg=BTN_COLOR.get(), fg=TEXT_COLOR.get(), font=("Arial", 12))
    bg_menu.pack(pady=5)

    back_button = styled_button(window, "Back to Menu", show_menu)
    back_button.pack(pady=20)

def show_menu():
    global running
    running = False

    for widget in window.winfo_children():
        widget.destroy()

    window.configure(bg=BG_COLOR.get())

    title = Label(window, text="Hand Sign App", font=("Arial", 28, "bold"), bg=BG_COLOR.get(), fg=TEXT_COLOR.get())
    title.pack(pady=40)

    detect_button = styled_button(window, "Start Detection", start_detection)
    detect_button.pack(pady=15)

    settings_button = styled_button(window, "Settings", show_settings)
    settings_button.pack(pady=15)

    about_button = styled_button(window, "About", show_about)
    about_button.pack(pady=15)

    quit_button = styled_button(window, "Quit", window.quit)
    quit_button.pack(pady=15)

    note = Label(window, text="This is a prototype", font=("Arial", 12, "italic"), bg=BG_COLOR.get(), fg=NOTE_COLOR.get())
    note.pack(pady=5)

    explanation = Label(
        window,
        text="Detection speed and accuracy depend on your device specifications.",
        font=("Arial", 11),
        bg=BG_COLOR.get(),
        fg=NOTE_COLOR.get()
    )
    explanation.pack(side="bottom", pady=10)

def show_loading():
    for widget in window.winfo_children():
        widget.destroy()

    loading_label = Label(window, text="Loading model...", font=("Arial", 20, "bold"), bg=BG_COLOR.get(), fg=TEXT_COLOR.get())
    loading_label.pack(expand=True)

def load_model():
    global model
    model = YOLO("best.pt")
    window.after(0, show_menu)

window = tk.Tk()
window.title("Hand Sign Detection")
window.geometry("900x700")

cam_width = IntVar(value=640, master=window)
cam_height = IntVar(value=480, master=window)
BG_COLOR = StringVar(value="#1e1e2f", master=window)
BTN_COLOR = StringVar(value="#3a3a5c", master=window)
BTN_HOVER = StringVar(value="#50507a", master=window)
TEXT_COLOR = StringVar(value="#ffffff", master=window)
NOTE_COLOR = StringVar(value="#aaaaaa", master=window)

window.configure(bg=BG_COLOR.get())

show_loading()

threading.Thread(target=load_model, daemon=True).start()

window.mainloop()

if cap:
    cap.release()