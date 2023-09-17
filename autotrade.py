import os
import shutil
import pyautogui
import time
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading
import keyboard
from tkinter import Entry, Label


# Global variables
selected_item_images = {}
is_trading = False
default_folder = './default_images/'
is_auto_chatting = False
item_position = None  # Store the position of the selected item



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
                    # Get screen dimensions
                    screen_width, screen_height = pyautogui.size()

                    # Calculate region: the whole width but only 200 pixels from the bottom of the screen
                    region_to_search_for_item = (0, screen_height - 200, screen_width, 200)

                    # Then update this line in your start_trading function
                    item_location = pyautogui.locateOnScreen(image_path, confidence=0.8, region=region_to_search_for_item)

                    if item_location:
                        print(f"Found item: {image_path}")
                        # click logic here
                        # Calculate coordinates for right-click
                        right_click_x = item_location.left - 15  # 10 pixels to the left
                        right_click_y = item_location.top + item_location.height // 2  # Middle of the height
                        
                        # Perform the right-click
                        pyautogui.rightClick(right_click_x, right_click_y)
                        
                        # Wait for the menu to appear
                        #click trade
                        time.sleep(1)
                        trade_location = pyautogui.locateOnScreen('click_trade.jpg', confidence=0.7)
                        if trade_location:
                            #time.sleep(0.1)
                            pyautogui.moveTo(trade_location)
                            pyautogui.click(trade_location)
                            print("Clicked trade")
                            #stop_trading()
                        
                        
        time.sleep(1)

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
root.title("DND Trading Bot")
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
keyboard.add_hotkey('F9', start_trading)


stop_button = tk.Button(root, text="Stop Trading", command=stop_trading)
stop_button.pack(pady=5)  # 5px gap
keyboard.add_hotkey('F8', stop_trading)

refresh_images()

inner_frame.update_idletasks()
frame.config(width=inner_frame.winfo_width() + scrollbar.winfo_width(), height=inner_frame.winfo_height())
canvas.config(scrollregion=canvas.bbox('all'))




# Function to capture the item position
def capture_item_position(e):
    global item_position
    item_position = pyautogui.position()
    print(f"Captured item position: {item_position}")

# Function to start auto-chat
def start_auto_chat():
    global is_auto_chatting, item_position
    chat_text = chat_entry.get()

    print("Please Shift + Left-Click the item you want to link in chat.")
    while item_position is None:
        time.sleep(1)
    print("Item position captured. Starting auto-chat.")

    is_auto_chatting = True
    while is_auto_chatting:
        if item_position:
            pyautogui.moveTo(item_position.x, item_position.y)
            time.sleep(0.5)  # Pause for a moment

            keyboard.press('shift')  # Press and hold shift using keyboard library
            time.sleep(0.2)  # Hold the Shift key down for a bit longer

            pyautogui.mouseDown(button='left')  # Mouse down using pyautogui
            time.sleep(0.2)  # Allow time for the click to register
            pyautogui.mouseUp(button='left')  # Mouse up using pyautogui

            keyboard.release('shift')  # Release shift using keyboard library
            time.sleep(0.2)  # Release the Shift key after a moment
        # Locate the chat box
            chat_box_location = pyautogui.locateOnScreen('chat_box.jpg', confidence=0.8)
            
            if chat_box_location:
                # Calculate the coordinates to click 100 pixels to the left of the chat box
                click_x = chat_box_location.left - 100
                click_y = chat_box_location.top + chat_box_location.height // 2  # Middle of the height
                
                # Click the calculated coordinates
                pyautogui.click(x=click_x, y=click_y)
                
                # Type the chat text and send it
                time.sleep(1)
                pyautogui.typewrite(chat_text)
                pyautogui.press('enter')  # Press enter to send the message
            
            time.sleep(10)  # Adjust the timing as needed


def stop_auto_chat():
    global is_auto_chatting, item_position  # Declare item_position as global
    is_auto_chatting = False
    item_position = None  # Reset the item position
    print("Stopped auto chat and cleared item position.")


# Inside your GUI setup code, add these elements:

# Label for chat text
chat_label = Label(root, text="Chat Text:")
chat_label.pack(pady=5)

# Entry box for chat text
chat_entry = Entry(root, width=30)
chat_entry.pack(pady=5)
chat_entry.insert(0, "50g")  # Default text

# Start auto chat button
start_chat_button = tk.Button(root, text="Start Auto Chat", command=lambda: threading.Thread(target=start_auto_chat).start())
start_chat_button.pack(pady=5)

# Stop auto chat button
stop_chat_button = tk.Button(root, text="Stop Auto Chat", command=stop_auto_chat)
stop_chat_button.pack(pady=5)

# Bind Shift+Mouse1 to capture the item position
keyboard.on_press_key('shift', capture_item_position, suppress=False)


keyboard.add_hotkey('F8', stop_auto_chat)


root.mainloop()