import os
import shutil
import pyautogui
import time
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading
import keyboard
import pytesseract
import queue
import cv2
import numpy as np

import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')  # Replace 'en_US.UTF-8' with your locale

from tkinter import ttk
from ttkbootstrap import Style

from tkinter import Entry, Label


# Global variables
selected_item_images = {}
is_trading = False
default_folder = './default_images/'
is_auto_chatting = False
item_position = None  # Store the position of the selected item
chat_text = None  # Store the chat text
is_monitoring_trade_room = False  # A global flag
debug_windows = {}  # Initialize debug_windows here as an empty dictionary
last_debug_coordinates = {}


##################### Debugging start #######################################
is_debug_mode = False
debug_window = None
debug_thread = None
debug_queue = queue.Queue()

## TKINTER GUI

root = tk.Tk()

# Function to read image and extract value
from PIL import ImageEnhance, ImageFilter

def read_test_image():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path

    test_image_path = "test_im.png"  # Replace with the path to your test image
    test_image = Image.open(test_image_path)

    # Image preprocessing
    test_image = test_image.convert('L')  # Convert to grayscale
    test_image = test_image.filter(ImageFilter.SHARPEN)  # Apply sharpen filter
    enhancer = ImageEnhance.Contrast(test_image)
    test_image = enhancer.enhance(2)  # Increase contrast
    test_image.save('debug_image.png')  # Save the image for debugging
    
    # Perform OCR on the test image
    custom_oem_psm_config = r'--oem 3 --psm 6'
    extracted_text = pytesseract.image_to_string(test_image, config=custom_oem_psm_config).strip()

    # Display the result in a new Tkinter window
    result_window = tk.Toplevel(root)
    result_window.title("OCR Result")
    
    result_label = tk.Label(result_window, text=f"Extracted Text: {extracted_text}")
    result_label.pack(pady=10)



def toggle_debug_mode():
    global is_debug_mode, debug_windows, debug_thread, debug_queue

    if is_debug_mode:
        for name, window in debug_windows.items():
            window.destroy()
        debug_windows.clear()
        is_debug_mode = False
        print("Debug mode disabled.")
    else:
        is_debug_mode = True
        print("Debug mode enabled.")
        if debug_thread is None:
            debug_thread = threading.Thread(target=update_debug_square_position, args=(debug_queue,))
            debug_thread.daemon = True  # Set as a daemon thread
            debug_thread.start()


        
def create_debug_window(width, height):
    window = tk.Toplevel(root)
    window.overrideredirect(True)
    window.wm_attributes("-alpha", 0.3)  # Make window transparent

    canvas = tk.Canvas(window, bg="blue", width=width, height=height)
    canvas.pack()
    canvas.create_rectangle(0, 0, width, height, outline="red", width=2)

    return window

def update_debug_square_position(q):
    global debug_windows, is_debug_mode, last_debug_coordinates

    while True:
        if is_debug_mode:
            # Your code to calculate the current coordinates
            current_coordinates = {
                'region_to_search_for_item': (0, 400, 800, 200),
                'gold_value_location': (815, 345, 100, 20)
            }

            # Check if coordinates have changed
            if current_coordinates != last_debug_coordinates:
                q.put(current_coordinates)
                last_debug_coordinates = current_coordinates  # Update last known coordinates

        time.sleep(0.1)

def check_queue():
    try:
        while True:
            data = debug_queue.get_nowait()
            # Update your Tkinter GUI here based on 'data'
            for area_name, coords in data.items():
                x, y, width, height = coords
                if area_name not in debug_windows:
                    debug_windows[area_name] = create_debug_window(width, height)
                debug_windows[area_name].geometry(f"{width}x{height}+{x}+{y}")
    except queue.Empty:
        pass
    root.after(100, check_queue)  # Check the queue every 100ms


############### DEBUGING END #########################################

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
                    region_to_search_for_item = (0, screen_height - 200, screen_width, 100)
                    debug_queue.put({'region_to_search_for_item': region_to_search_for_item})
                    # Then update this line in your start_trading function
                    item_location = pyautogui.locateOnScreen(image_path, confidence=0.8, region=region_to_search_for_item)
                    

                    # Update debug window directly
                    if is_debug_mode:
                        debug_queue.put({'region_to_search_for_item': region_to_search_for_item})



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
                        time.sleep(0.1)
                        trade_location = pyautogui.locateOnScreen('click_trade.jpg', confidence=0.7)
                        if trade_location:
                            #time.sleep(0.1)
                            pyautogui.moveTo(trade_location)
                            pyautogui.click(trade_location)
                            print("Clicked trade")
                            #stop_trading()
                        
                        
        time.sleep(0.3)

def stop_trading():
    global is_trading
    is_trading = False
    print("Stopped trading.")



# Function to capture the item position
def capture_item_position(e):
    global item_position
    item_position = pyautogui.position()
    print(f"Captured item position: {item_position}")
    
    
 
    
def monitor_trade_room(chat_entry):
    global is_monitoring_trade_room, item_position
    is_monitoring_trade_room = True
    while is_monitoring_trade_room:  # Check the flag here
        # Check if you're in a private trading room
        #pvroom_location = pyautogui.locateOnScreen('pvtroom2.jpg', confidence=0.8)
        #pvroom_location2 = pyautogui.locateOnScreen('pvtroom.png', confidence=0.8)
        pvroom_location = pyautogui.locateOnScreen('pvtroom3.jpg', confidence=0.8)
        if pvroom_location:
            print("You are in a private trading room.")
            
            # Check the phase of the trade
            phase1_location = pyautogui.locateOnScreen('trading_phase1.png', confidence=0.8)
            phase2_location = pyautogui.locateOnScreen('trading_phase2.png', confidence=0.8)
            hardcoded_coordinates = (815, 345, 100, 20)
            
            if phase1_location:
                print("Phase 1 detected.")
                            # Directly put hardcoded coordinates into the debug queue
                if is_debug_mode:
                    debug_queue.put({'gold_value_location': hardcoded_coordinates})
                    
                    

                # Use OCR to read the value
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                gold_value = pyautogui.screenshot(region=hardcoded_coordinates)

                # Convert PIL Image to NumPy array
                gold_value_np = np.array(gold_value)
                
                # Convert RGB to Grayscale
                gray = cv2.cvtColor(gold_value_np, cv2.COLOR_BGR2GRAY)
                
                # Convert NumPy array to PIL Image
                gray_image = Image.fromarray(gray)

                # Save the screenshot for debugging
                gray_image.save("debug_screenshot_gray.png")


                # Custom Tesseract Configuration
                custom_oem_psm_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
                gold_value_text = pytesseract.image_to_string(gray_image, config=custom_oem_psm_config).strip()

                if gold_value_text:
                    print(f"Gold value region captured: {gold_value_text}")

                    entry_value = chat_entry.get()  # Get the value from the Tkinter entry box
                    if entry_value == gold_value_text:  # Convert gold_value_text to integer
                        print("Gold value matches or is higher than the set entry value. Proceeding to click.")
                        
                        
                        # Your code to click on an image goes here
                        # For example, locate and click on an "Accept" button
                        accept_button_location = pyautogui.locateOnScreen('greycheck.png', confidence=0.8)
                        if accept_button_location:
                            pyautogui.click(accept_button_location)
                            time.sleep(5)
                            
                            pyautogui.click(703, 319)
                            time.sleep(0.1)
                            pyautogui.click(752, 328)
                            time.sleep(0.1)
                            pyautogui.click(793, 332)
                            time.sleep(0.1)
                            pyautogui.click(839, 328)
                            time.sleep(0.1)
                            pyautogui.click(706, 375)
                            time.sleep(0.1)
                            pyautogui.click(752, 375)
                            time.sleep(0.1)
                            pyautogui.click(794, 375)
                            time.sleep(0.1)
                            pyautogui.click(842, 375)
                            time.sleep(0.1)
                            pyautogui.click(887, 375)
                            
                            time.sleep(1)
                        
                            accept_button_location = pyautogui.locateOnScreen('greycheck.png', confidence=0.8)
                            if accept_button_location:
                                pyautogui.click(accept_button_location)
                                time.sleep(3)

                    else:
                        print("Gold value does not match the set entry value.")
                        #keyboard.press('esc')  # Press the Esc key to stop the trade
                        #stop_monitoring_trade_room()
                else:
                    print("No text captured.")

                
            
            if phase2_location:
                print("Phase 2 detected.")
                # Check for the total gold value

                if is_debug_mode:
                    debug_queue.put({'gold_value_location': hardcoded_coordinates})

                # Use OCR to read the value
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                gold_value = pyautogui.screenshot(region=hardcoded_coordinates)

                # Convert PIL Image to NumPy array
                gold_value_np = np.array(gold_value)
                
                # Convert RGB to Grayscale
                gray = cv2.cvtColor(gold_value_np, cv2.COLOR_BGR2GRAY)
                
                # Convert NumPy array to PIL Image
                gray_image = Image.fromarray(gray)

                # Save the screenshot for debugging
                gray_image.save("debug_screenshot_gray.png")


                # Custom Tesseract Configuration
                custom_oem_psm_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
                gold_value_text = pytesseract.image_to_string(gray_image, config=custom_oem_psm_config).strip()


                if gold_value_text:
                    print(f"Gold value region captured PHASE 2: {gold_value_text}")
                    entry_value = chat_entry.get()  # Get the value from the Tkinter entry box
                    if entry_value == gold_value_text:  # Convert gold_value_text to integer
                        print("Gold value matches or is higher than the set entry value. Proceeding to click PHASE2")
                        pyautogui.click(703, 319)
                        time.sleep(0.1)
                        pyautogui.click(752, 328)
                        time.sleep(0.1)
                        pyautogui.click(793, 332)
                        time.sleep(0.1)
                        pyautogui.click(839, 328)
                        time.sleep(0.1)
                        pyautogui.click(706, 375)
                        time.sleep(0.1)
                        pyautogui.click(752, 375)
                        time.sleep(0.1)
                        pyautogui.click(794, 375)
                        time.sleep(0.1)
                        pyautogui.click(842, 375)
                        time.sleep(0.1)
                        pyautogui.click(887, 375)
                        
                        time.sleep(1)
                        
                        accept_button_location = pyautogui.locateOnScreen('greycheck.png', confidence=0.8)
                        if accept_button_location:
                            pyautogui.click(accept_button_location)
                            time.sleep(3)
                    else:
                        print("Gold value does not match the set entry value.")
                        #keyboard.press('esc')  # Press the Esc key to stop the trade
                        #stop_monitoring_trade_room()
                else:
                    print("No text captured.")
            
            time.sleep(1)  # Check every second or adjust this timing as needed
        else:
            print("You are not in a private trading room.")
            break  # Exit the loop if not in a private room

def stop_monitoring_trade_room():
    global is_monitoring_trade_room
    is_monitoring_trade_room = False
    print("Stopped monitoring trade room.")


# Function to start auto-chat
def start_auto_chat(chat_entry):
    global is_auto_chatting, item_position
    chat_text = chat_entry.get() + "g"  # Automatically append "g"

    print("Please Shift + Left-Click the item you want to link in chat.")
    while item_position is None:
        time.sleep(1)
    print("Item position captured. Starting auto-chat.")

    is_auto_chatting = True
    while is_auto_chatting:
                # Check for trade request
        trade_request_location = pyautogui.locateOnScreen('trade_request.jpg', confidence=0.8)
        if trade_request_location:
            print("Trade request detected. Stopping auto chat.")
            yes_location = pyautogui.locateOnScreen('yes.png', confidence=0.8)
            if yes_location:
                pyautogui.moveTo(yes_location)
                pyautogui.click(yes_location)
                print("Accepted trade request.")
                time.sleep(3)
                stash = pyautogui.locateOnScreen('stash.png', confidence=0.8)
                time.sleep(0.3)
                pyautogui.moveTo(stash)
                pyautogui.click(stash)
                
                    # Calculate the new x-coordinate for the trade phase
                new_trade_x = item_position.x + 318  # 318 is the offset
                new_trade_position = pyautogui.Point(new_trade_x, item_position.y)

            
                pyautogui.moveTo(new_trade_position)
                pyautogui.click(new_trade_position)
                
                monitor_trade_room(chat_entry)
            stop_auto_chat()  # Stop the auto chat
            return  # Exit the function
        
        
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
    #item_position = None  # Reset the item position
    chat_text = None
    print("Stopped auto chat and cleared item position.")


# Inside your GUI setup code, add these elements:
# Function to validate input for only numbers
def validate_input(P):
    if P == "" or P.isdigit():
        return True
    return False


validate_cmd = root.register(validate_input)


# Bind Shift+Mouse1 to capture the item position
keyboard.on_press_key('shift', capture_item_position, suppress=False)


keyboard.add_hotkey('F8', stop_auto_chat)





class TradingApp:
    def __init__(self, master, start_trading_callback, stop_trading_callback, start_auto_chat_callback, stop_auto_chat_callback, monitor_trade_room_callback, stop_monitoring_trade_room_callback, toggle_debug_mode_callback):
        try:
            self.master = master
            self.start_trading_callback = start_trading_callback
            self.stop_trading_callback = stop_trading_callback
            self.start_auto_chat_callback = start_auto_chat_callback
            self.stop_auto_chat_callback = stop_auto_chat_callback
            self.monitor_trade_room_callback = monitor_trade_room_callback
            self.stop_monitoring_trade_room_callback = stop_monitoring_trade_room_callback
            self.toggle_debug_mode_callback = toggle_debug_mode_callback

            self.master.title("The Old Trader")
            self.master.geometry("800x500")

            # Create themed Tkinter root
            self.style = Style()
            self.style.theme_use('cyborg')  # dark theme
            

            
            # Create the notebook (tabbed interface)
            self.notebook = ttk.Notebook(self.master)

            # Create frames for each tab
            self.tab_auto_sell = ttk.Frame(self.notebook)
            self.tab_auto_trade = ttk.Frame(self.notebook)
            self.tab_development = ttk.Frame(self.notebook)

            # Add the frames as tabs to the notebook
            self.notebook.add(self.tab_auto_sell, text="Auto Sell")
            self.notebook.add(self.tab_auto_trade, text="Auto Trade")
            self.notebook.add(self.tab_development, text="Development")



            self.inner_frame = tk.Frame(self.tab_auto_trade)
            #
            self.inner_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            
            # Load button for images
            self.load_button = tk.Button(self.master, text="Load Item Image", command=self.load_item_image)
            self.load_button.pack(in_=self.tab_auto_trade, pady=5)

            self.refresh_images()
            
            
            keybind_info = (
                "SHIFT: Capture Item Position\n"
                "F8: Stop Auto Selling/Trading\n"
            )
            keybind_text = tk.Text(self.tab_auto_sell, height=6, width=30, wrap=tk.WORD, relief=tk.GROOVE)
            keybind_text.insert(tk.END, keybind_info)
            keybind_text.config(state=tk.DISABLED)  # Make it read-only
            keybind_text.pack(side=tk.BOTTOM, padx=5, pady=5)
        

            # Place the notebook on the Tkinter window
            self.notebook.pack(expand=True, fill='both')
            

            self.start_button = ttk.Button(self.master, text="Start Trading", command=lambda: threading.Thread(target=self.start_trading_callback).start())
            self.start_button.pack(in_=self.tab_auto_trade, pady=5)

            self.stop_button = ttk.Button(self.master, text="Stop Trading", command=self.stop_trading_callback)
            self.stop_button.pack(in_=self.tab_auto_trade, pady=5)
            
            self.chat_label = Label(root, text="Sell Price:")
            self.chat_label.pack(in_=self.tab_auto_sell, pady=(85,5))

            # Entry box for chat text
            self.chat_entry = ttk.Entry(root, validate="key", validatecommand=(validate_cmd, '%P'), width=30, bootstyle='success')
            self.chat_entry.pack(in_=self.tab_auto_sell, pady=5)
            self.chat_entry.insert(0, "50")  # Default text

            #keyboard.add_hotkey('F7', start_auto_chat, args=(self.chat_entry,))
            

            self.start_chat_button = ttk.Button(self.master, text="Start Auto Sell", command=lambda: threading.Thread(target=self.start_auto_chat_callback, args=(self.chat_entry,)).start())
            self.start_chat_button.pack(in_=self.tab_auto_sell, pady=5)

            self.stop_chat_button = ttk.Button(self.master, text="Stop Auto Sell", command=self.stop_auto_chat_callback)
            self.stop_chat_button.pack(in_=self.tab_auto_sell, pady=5)

            self.test_button = ttk.Button(self.master, text="Test Trade Room", command=lambda: threading.Thread(target=self.monitor_trade_room_callback).start())
            self.test_button.pack(in_=self.tab_development, pady=5)

            self.stop_monitor_button = ttk.Button(self.master, text="Stop Monitoring Trade Room", command=self.stop_monitoring_trade_room_callback)
            self.stop_monitor_button.pack(in_=self.tab_development, pady=5)

            self.debug_button = ttk.Button(self.master, text="Toggle Debug", command=self.toggle_debug_mode_callback)
            self.debug_button.pack(in_=self.tab_development, pady=5)
            
        except Exception as e:
            print(e)

            # More widgets and initialization code here...
    def refresh_images(self):
            for widget in self.inner_frame.winfo_children():
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

                    img_button = tk.Button(self.inner_frame, image=img, relief=tk.RAISED)
                    img_button.image = img
                    img_button.grid(row=row, column=col)
                    img_button.config(command=lambda img_path=img_path, img_button=img_button: self.toggle_image_selection(img_path, img_button))

                    col += 1
                    if col > 7:  # 4 images per row
                        col = 0
                        row += 1

    def load_item_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
        if file_path:
            shutil.copy(file_path, default_folder)
            self.refresh_images()
            
            
    def toggle_image_selection(self, image_path, button):
        global selected_item_images  # If this variable is not class-wide, consider making it an instance variable.
        is_selected = selected_item_images.get(image_path, False)
        selected_item_images[image_path] = not is_selected
        if not is_selected:
            button.config(relief=tk.SUNKEN)  # Indicate the image is selected
        else:
            button.config(relief=tk.RAISED)  # Indicate the image is deselected
        print(f"Toggled selection for {image_path}: {not is_selected}")



app = TradingApp(
    root, 
    start_trading, 
    stop_trading, 
    start_auto_chat, 
    stop_auto_chat, 
    monitor_trade_room, 
    stop_monitoring_trade_room,
    toggle_debug_mode
)


root.after(100, check_queue)
root.mainloop()

