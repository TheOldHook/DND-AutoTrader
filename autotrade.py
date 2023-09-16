import os
import pyautogui
import time
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading

# Global variables
selected_item_images = {}  # Dictionary to keep track of selected items
is_trading = False
default_folder = './default_images/'  # Replace with the path to your default folder

def start_trading():
    global selected_item_images, is_trading

    if not selected_item_images:
        print("No items selected for trading.")
        return

    print(f"Starting trading in 5 seconds...")
    time.sleep(5)

    is_trading = True
    while is_trading:
        chat_area = pyautogui.locateOnScreen('chat_area.jpg', confidence=0.8)
        if chat_area:
            for image_path, is_selected in selected_item_images.items():
                if is_selected:
                    item_location = pyautogui.locateOnScreen(image_path, confidence=0.8)
                    if item_location:
                        print(f"Found item: {image_path}")
                        # Your drag and click logic here
        time.sleep(2)

def stop_trading():
    global is_trading
    is_trading = False
    print("Stopped trading.")

def toggle_image_selection(image_path, button):
    global selected_item_images
    is_selected = selected_item_images.get(image_path, False)
    selected_item_images[image_path] = not is_selected
    if not is_selected:
        button.config(relief=tk.SUNKEN)  # Indicate the image is selected
    else:
        button.config(relief=tk.RAISED)  # Indicate the image is deselected
    print(f"Toggled selection for {image_path}: {not is_selected}")

# GUI setup
root = tk.Tk()
root.title("Auto Trading Bot")
root.geometry("600x400")  # Set window dimensions

load_button = tk.Button(root, text="Load Item Image", command=filedialog.askopenfilename)
load_button.pack()

start_button = tk.Button(root, text="Start Trading", command=lambda: threading.Thread(target=start_trading).start())
start_button.pack()

stop_button = tk.Button(root, text="Stop Trading", command=stop_trading)
stop_button.pack()

# Automatically show images from the default folder
if os.path.exists(default_folder):
    for filename in os.listdir(default_folder):
        if filename.endswith('.jpg') or filename.endswith('.png'):
            img_path = os.path.join(default_folder, filename)
            img = Image.open(img_path)
            img = img.resize((50, 50), Image.LANCZOS)  # Changed to LANCZOS due to deprecation warning
            img = ImageTk.PhotoImage(img)
            img_button = tk.Button(root, image=img, relief=tk.RAISED)
            img_button.image = img  # Keep a reference to prevent GC
            img_button.pack(side=tk.LEFT)
            img_button.config(command=lambda img_path=img_path, img_button=img_button: toggle_image_selection(img_path, img_button))  # Moved the command here

root.mainloop()
