import os
import shutil
import pyautogui
import time
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading

# Global variables
selected_item_images = {}
is_trading = False
default_folder = './default_images/'

if not os.path.exists(default_folder):
    os.makedirs(default_folder)

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
                        # click logic here
                        # Calculate coordinates for right-click
                        right_click_x = item_location.left - 10  # 10 pixels to the left
                        right_click_y = item_location.top + item_location.height // 2  # Middle of the height
                        
                        # Perform the right-click
                        pyautogui.rightClick(right_click_x, right_click_y)
                        
                        # Wait for the menu to appear
                        #click trade
                        time.sleep(1)
                        trade_location = pyautogui.locateOnScreen('click_trade.jpg', confidence=0.8)
                        if trade_location:
                            time.sleep(0.1)
                            pyautogui.click(trade_location)
                            print("Clicked trade")
                            #stop_trading()
                        
                        
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
    
    

def load_item_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
    if file_path:
        shutil.copy(file_path, default_folder)
        refresh_images()
        
def refresh_images():
    global inner_frame
    for widget in inner_frame.winfo_children():
        widget.destroy()

    row, col = 0, 0
    for filename in os.listdir(default_folder):
        if filename.endswith(('.jpg', '.png')):
            img_path = os.path.join(default_folder, filename)
            img = Image.open(img_path)
            base_width = 100
            w_percent = base_width / float(img.size[0])
            h_size = int(float(img.size[1]) * float(w_percent))
            img = img.resize((base_width, h_size), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            
            img_button = tk.Button(inner_frame, image=img, relief=tk.RAISED)
            img_button.image = img
            img_button.grid(row=row, column=col)
            img_button.config(command=lambda img_path=img_path, img_button=img_button: toggle_image_selection(img_path, img_button))
            
            col += 1
            if col > 3:  # 4 images per row
                col = 0
                row += 1

# GUI setup
root = tk.Tk()
root.title("Auto Trading Bot")
root.geometry("600x400")

frame = tk.Frame(root)
frame.pack(side=tk.LEFT, padx=10, pady=10)

canvas = tk.Canvas(frame, width=450)  # Width adjusted to fit the grid
canvas.pack(side=tk.LEFT)

scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.LEFT, fill=tk.Y)

canvas.config(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.config(scrollregion=canvas.bbox('all')))

inner_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=inner_frame, anchor=tk.NW)

load_button = tk.Button(root, text="Load Item Image", command=load_item_image)
load_button.pack(pady=40)  # Moved down by 20px

start_button = tk.Button(root, text="Start Trading", command=lambda: threading.Thread(target=start_trading).start())
start_button.pack(pady=5)  # 5px gap

stop_button = tk.Button(root, text="Stop Trading", command=stop_trading)
stop_button.pack(pady=5)  # 5px gap

refresh_images()

inner_frame.update_idletasks()
frame.config(width=inner_frame.winfo_width() + scrollbar.winfo_width(), height=inner_frame.winfo_height())
canvas.config(scrollregion=canvas.bbox('all'))

root.mainloop()