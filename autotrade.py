import pyautogui
import time
import tkinter as tk
from tkinter import filedialog
import threading  # Import the threading module

# Global variables
selected_item_image = None
is_trading = False

def start_trading():
    global selected_item_image, is_trading
    if selected_item_image is None:
        print("No item selected for trading.")
        return

    print(f"Starting trading with {selected_item_image} in 5 seconds...")
    time.sleep(5)

    is_trading = True
    while is_trading:
        chat_area = pyautogui.locateOnScreen('chat_area.jpg', confidence=0.8)
        if chat_area:
            item_location = pyautogui.locateOnScreen(selected_item_image, confidence=0.8)
            if item_location:
                print(f"Found item: {selected_item_image}")
                # Your drag and click logic here
        time.sleep(2)

def stop_trading():
    global is_trading
    is_trading = False
    print("Stopped trading.")

def load_item_image():
    global selected_item_image
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
    if file_path:
        selected_item_image = file_path
        print(f"Selected item image: {file_path}")

# GUI setup
root = tk.Tk()
root.title("DND AutoTrader")

load_button = tk.Button(root, text="Load Item Image", command=load_item_image)
load_button.pack()

# Start the start_trading function in a new thread
start_button = tk.Button(root, text="Start Trading", command=lambda: threading.Thread(target=start_trading).start())
start_button.pack()

stop_button = tk.Button(root, text="Stop Trading", command=stop_trading)
stop_button.pack()

root.mainloop()
