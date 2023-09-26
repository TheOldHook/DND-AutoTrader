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
import uuid

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
is_shift_pressed = False
is_stop_pressed = False

# For dropdown menus
class_list = ["Fighter", "Wizard", "Ranger", "Rogue", "Cleric", "Bard", "Barbarian", "Warlock", "Utility"]

##################### Debugging start #######################################
is_debug_mode = False
debug_window = None
debug_thread = None
debug_queue = queue.Queue()

## 
global successful_sales, total_gold
successful_sales = 0
total_gold = 0


root = tk.Tk()

# Function to read image and extract value
from PIL import ImageEnhance, ImageFilter

def read_test_image():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path

    test_image_path = "./image_locations/test_im.png"  # Replace with the path to your test image
    test_image = Image.open(test_image_path)

    # Image preprocessing
    test_image = test_image.convert('L')  # Convert to grayscale
    test_image = test_image.filter(ImageFilter.SHARPEN)  # Apply sharpen filter
    enhancer = ImageEnhance.Contrast(test_image)
    test_image = enhancer.enhance(2)  # Increase contrast
    test_image.save('./image_locations/debug_image.png')  # Save the image for debugging
    
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
        chat_area = pyautogui.locateOnScreen('./image_locations/chat_area.jpg', confidence=0.8)
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
                        trade_location = pyautogui.locateOnScreen('./image_locations/click_trade.jpg', confidence=0.7)
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
def capture_item_position(self, e):
    global item_position  # Declare it as global so you can modify it
    position = pyautogui.position()
    print(f"Captured item position: {position}")
    print(self.sell_option_var.get())

    # If Multi-Sell is selected
    if self.sell_option_var.get() == '2':
        new_entry = {
            "RowId": str(uuid.uuid4()),  # Generate a unique ID for each entry
            "Position": position,
            "Item": "Gear",
            "Class": "Ranger",  # Set the default value as a string
            "Price": "100",
            "Status": ""
        }
        self.multi_item_positions.append(new_entry)
        self.update_table()  # Update the table in the GUI
    else:
        item_position = position



    
    
 
    
def monitor_trade_room(chat_entry, current_row):
    global is_monitoring_trade_room, item_position, is_debug_mode, debug_queue, is_auto_chatting, is_stop_pressed
    global successful_sales, total_gold

    is_auto_chatting = False
    is_monitoring_trade_room = True
    while is_monitoring_trade_room:  # Check the flag here
        # Check if you're in a private trading room
        #pvroom_location = pyautogui.locateOnScreen('pvtroom2.jpg', confidence=0.8)
        #pvroom_location2 = pyautogui.locateOnScreen('pvtroom.png', confidence=0.8)
        pvroom_location = pyautogui.locateOnScreen('./image_locations/pvtroom3.jpg', confidence=0.8)
        if pvroom_location:
            print("You are in a private trading room.")
            
            stash = pyautogui.locateOnScreen('./image_locations/stash.png', confidence=0.8)
            time.sleep(0.3)
            pyautogui.moveTo(stash)
            pyautogui.click(stash)
            
            # Check the phase of the trade
            phase1_location = pyautogui.locateOnScreen('./image_locations/trading_phase1.png', confidence=0.8)
            phase2_location = pyautogui.locateOnScreen('./image_locations/trading_phase2.png', confidence=0.8)
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
                gray_image.save("./image_locations/debug_screenshot_gray.png")


                # Custom Tesseract Configuration
                custom_oem_psm_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
                gold_value_text = pytesseract.image_to_string(gray_image, config=custom_oem_psm_config).strip()

                if gold_value_text:
                    print(f"Gold value region captured: {gold_value_text}")

                    # Check the type of chat_entry and get entry_value accordingly
                    if isinstance(chat_entry, tk.Entry):  # If it's a Tkinter Entry widget
                        entry_value = chat_entry.get()
                        print("Entry value: FROM TK ", entry_value)
                    elif isinstance(chat_entry, str):  # If it's a string
                        entry_value = chat_entry
                        print("Entry value: FROM STRING ", entry_value)
                    else:
                        print("Unsupported type for chat_entry")
                        return  # Or handle this case as you see fit

                    if entry_value == gold_value_text:  # Convert gold_value_text to integer
                        print("Gold value matches or is higher than the set entry value. Proceeding to click.")
                        
                        
                        # Your code to click on an image goes here
                        # For example, locate and click on an "Accept" button
                        accept_button_location = pyautogui.locateOnScreen('./image_locations/greycheck.png', confidence=0.8)
                        if accept_button_location:
                            pyautogui.click(accept_button_location)
                            print("Clicked accept the greybutton.")
                            time.sleep(5)
                            
                            pyautogui.click(703, 319)
                            time.sleep(0.1)
                            pyautogui.click(752, 328)
                            time.sleep(0.1)
                            pyautogui.click(793, 332)
                            time.sleep(0.1)
                            pyautogui.click(839, 328)
                            time.sleep(0.1)
                            pyautogui.click(887, 328)
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
                            time.sleep(0.1)
                            pyautogui.click(703, 415)
                            time.sleep(0.1)
                            pyautogui.click(752, 415)
                            time.sleep(0.1)
                            pyautogui.click(793, 415)
                            time.sleep(0.1)
                            pyautogui.click(839, 415)
                            time.sleep(0.1)
                            pyautogui.click(887, 415)
                            time.sleep(0.1)
                            pyautogui.click(703, 468)
                            time.sleep(0.1)
                            pyautogui.click(752, 468)
                            time.sleep(0.1)
                            pyautogui.click(793, 468)
                            time.sleep(0.1)
                            pyautogui.click(839, 468)
                            time.sleep(0.1)
                            pyautogui.click(887, 468)
                            time.sleep(0.1)
                            pyautogui.click(703, 510)
                            time.sleep(0.1)
                            pyautogui.click(703, 510)
                            time.sleep(0.1)
                            pyautogui.click(755, 513)
                            time.sleep(0.1)
                            pyautogui.click(801, 513)
                            time.sleep(0.1)
                            pyautogui.click(841, 512)
                            time.sleep(0.1)
                            pyautogui.click(886, 513)
                            print("Clicked on the money locations.")
                            
                            time.sleep(1)
                        
                            accept_button_location = pyautogui.locateOnScreen('./image_locations/greycheck.png', confidence=0.8)
                            if accept_button_location:
                                pyautogui.click(accept_button_location)
                                time.sleep(3)
                                successful_sales += 1
                                total_gold += int(entry_value)
                                current_row['Status'] = 'Sold'
                                app.update_ui(successful_sales, total_gold)
                                print("Successful sales!!")
                                time.sleep(3)
                                is_stop_pressed = False
                                return
                            else:
                                print("No accept button found")
                                current_row['Status'] = 'Failed'
                        else:
                            print("No accept button found")
                            current_row['Status'] = 'Failed'

                    else:
                        print("Gold value does not match the set entry value.")
                        #keyboard.press('esc')  # Press the Esc key to stop the trade
                        #stop_monitoring_trade_room()
                else:
                    print("No text captured.")
                    
            time.sleep(1)  # Check every second or adjust this timing as needed
            if is_stop_pressed is True:
                print("Stop pressed. Exiting loop.")
                break  # Exit the loop
            
        else:
            print("You are not in a private trading room.")
            stop_monitoring_trade_room()  # Stop monitoring the trade room
            app.start_sell_thread()
            break  # Exit the loop if not in a private room

def stop_monitoring_trade_room():
    global is_monitoring_trade_room
    is_monitoring_trade_room = False
    print("Stopped monitoring trade room.")


# Function to start auto-chat
def start_auto_chat(chat_entry, multi_item_positions, current_row):
    global is_auto_chatting, item_position, is_stop_pressed
    is_stop_pressed = False
    #chat_text = chat_entry.get() + "g"  # Automatically append "g"
    
    item_position = multi_item_positions
    # Check the type of chat_entry and act accordingly
    if hasattr(chat_entry, 'get'):
        chat_text = " " + chat_entry.get() + "g"  # Automatically append "g"
    else:
        chat_text = " " + chat_entry + "g"  # Assume it's a string and append "g"

    while item_position is None:
        time.sleep(1)
    print("Item position captured. Starting auto-chat.")

    is_auto_chatting = True
    while is_auto_chatting:
                # Check for trade request
        trade_request_location = pyautogui.locateOnScreen('./image_locations/trade_request.jpg', confidence=0.8)
        if trade_request_location:
            print("Trade request detected. Stopping auto chat.")
            yes_location = pyautogui.locateOnScreen('./image_locations/yes.png', confidence=0.8)
            if yes_location:
                pyautogui.moveTo(yes_location)
                pyautogui.click(yes_location)
                print("Accepted trade request.")
                time.sleep(3)
                stash = pyautogui.locateOnScreen('./image_locations/stash.png', confidence=0.8)
                time.sleep(0.3)
                pyautogui.moveTo(stash)
                pyautogui.click(stash)
                print("Clicked stash")
                time.sleep(3)
                
                    # Calculate the new x-coordinate for the trade phase
                new_trade_x = item_position.x + 318  # 318 is the offset
                new_trade_position = pyautogui.Point(new_trade_x, item_position.y)

            
                pyautogui.moveTo(new_trade_position)
                pyautogui.click(new_trade_position)
                print("Clicked on new trade position")
                
                monitor_trade_room(chat_entry, current_row)
            stop_auto_chat()  # Stop the auto chat
            return  # Exit the function
        
        
        if item_position:
            pyautogui.moveTo(item_position.x, item_position.y)
            time.sleep(1)  # Pause for a moment

            keyboard.press('shift')  # Press and hold shift using keyboard library
            time.sleep(1)  # Hold the Shift key down for a bit longer
            
            pyautogui.moveTo(item_position.x, item_position.y)
            time.sleep(0.1)  # Pause for a moment
            pyautogui.click(item_position.x, item_position.y)  # Click the item using pyautogui

            # pyautogui.mouseDown(button='left')  # Mouse down using pyautogui
            # time.sleep(1)  # Allow time for the click to register
            # pyautogui.mouseUp(button='left')  # Mouse up using pyautogui

            keyboard.release('shift')  # Release shift using keyboard library
            time.sleep(0.2)  # Release the Shift key after a moment
            
            # Locate the chat box
            chat_box_location = pyautogui.locateOnScreen('./image_locations/chat_box.jpg', confidence=0.8)
            
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
        else:
            print("No item position found. Stopping auto chat.")
            stop_auto_chat()  # Stop the auto chat

            

def stop_auto_chat():
    global is_auto_chatting, item_position, is_stop_pressed  # Declare item_position as global
    is_auto_chatting = False
    #item_position = None  # Reset the item position
    chat_text = None
    is_stop_pressed = True

    print("Stopped auto chat and cleared item position.")


# Inside your GUI setup code, add these elements:
# Function to validate input for only numbers
def validate_input(P):
    if P == "" or P.isdigit():
        return True
    return False


validate_cmd = root.register(validate_input)


# Keybindings
#keyboard.on_press_key('shift', capture_item_position, suppress=False)
keyboard.add_hotkey('F8', stop_auto_chat)


def goto_class(item_class):
    print("Class:", item_class)
    #print("Navigating to class trade chat...")
    
    chat_area = pyautogui.locateOnScreen('./image_locations/chat_area.jpg', confidence=0.8)
    if chat_area:
        
        leave_channel = pyautogui.locateOnScreen('./image_locations/leave_channel.png', confidence=0.8)
        if leave_channel:
            pyautogui.moveTo(leave_channel)
            pyautogui.click(leave_channel)
            time.sleep(0.1)
            yes = pyautogui.locateOnScreen('./image_locations/yes.png', confidence=0.8)
            if yes:
                pyautogui.moveTo(yes)
                pyautogui.click(yes)
                time.sleep(2)
                select_channel = pyautogui.locateOnScreen('./image_locations/select_channel.png', confidence=0.8)
                if select_channel:
                
                    if item_class == "Fighter":
                        print("Navigating to Fighter trade chat...")
                        pyautogui.moveTo(1193, 287)
                        pyautogui.click(1193, 287)
                        time.sleep(3)
                        
                        
                    elif item_class ==  "Wizard":
                        print("Navigating to Wizard trade chat...")
                        pyautogui.moveTo(1205, 595)
                        pyautogui.click(1205, 595)
                        time.sleep(3)
                        
                    elif item_class ==  "Ranger":
                        print("Navigating to Ranger trade chat...")
                        pyautogui.moveTo(1188, 520)
                        pyautogui.click(1188, 520)
                        time.sleep(3)
                        
                    elif item_class ==  "Rogue":
                        print("Navigating to Rogue trade chat...")
                        pyautogui.moveTo(1190, 444)
                        pyautogui.click(1190, 444)
                        time.sleep(3)
                        
                    elif item_class ==  "Cleric":
                        print("Navigating to Cleric trade chat...")
                        pyautogui.moveTo(1193, 664)
                        pyautogui.click(1193, 664)
                        time.sleep(3)
                        
                    elif item_class ==  "Bard":
                        print("Navigating to Bard trade chat...")
                        pyautogui.moveTo(1184, 752)
                        pyautogui.click(1184, 752)
                        time.sleep(3)
                        
                    elif item_class ==  "Barbarian":
                        print("Navigating to Barbarian trade chat...")
                        pyautogui.moveTo(1188, 367)
                        pyautogui.click(1188, 367)
                        time.sleep(3)
                        
                    elif item_class ==  "Warlock":
                        print("Navigating to Warlock trade chat...")
                        pyautogui.moveTo(1173, 814)
                        pyautogui.click(1173, 814)
                        time.sleep(3)
                        
                    elif item_class ==  "Utility":
                        print("Navigating to Utility trade chat...")
                        pyautogui.moveTo(1185, 946)
                        pyautogui.click(1185, 946)
                        time.sleep(3)
                        
                else:
                    print("No select channel found")
            else:
                print("No yes found")
        else:
            print("No chat area found")
    else:
        print("No leave channel found")
    
    
    

    


def start_multi_sell(table_data):
    global is_auto_chatting, is_stop_pressed
    print("Starting multi selling...")
    print(f"Table data: {table_data}")
    
    for row in table_data:
        print(f"Current row data before processing: {row}")
        row_id = row['RowId']
        position = row['Position']
        item = row['Item']
        item_class = row['Class']
        price = row['Price']
        status = row['Status']
        is_auto_chatting = False

        # Set item_position in thread-local storage
        
        # Skip if already sold
        if status == 'Sold':
            print(f"Skipping Row ID: {row_id}, Status: Sold")
            continue  # Skip to the next iteration

        # Update status to 'Processing..'
        row['Status'] = 'Processing..'
        print(f"Processing Row ID: {row_id}, Status: {row['Status']}")
        
        try:
            app.update_table()  # Update the table in the GUI
        except Exception as e:
            print(f"An error occurred while updating the table: {e}")
        
        # Selling logic here, for example:
        # 1. Navigate to the position on screen to click on the item (use the 'position' variable)
        # 2. Input the item's class and price to sell it (use 'item_class' and 'price' variables)
        goto_class(item_class)
        
        time.sleep(3)
        stash = pyautogui.locateOnScreen('./image_locations/stash2.png', confidence=0.8)
        if stash:
            time.sleep(0.3)
            pyautogui.moveTo(stash)
            pyautogui.click(stash)
            time.sleep(3)
        else:
            print("No stash found")
        
        item_position = row['Position']
        item_position = item_position
        start_auto_chat(price, position, row)

        #row['Status'] = 'Sold'
        print(f"Row ID: {row_id}, Status: {row['Status']}")
        
        try:
            app.update_table()  # Update the table in the GUI
        except Exception as e:
            print(f"An error occurred while updating the table: {e}")

        # Check if auto chat should be stopped
        if is_stop_pressed is True:
            print("Auto chat stopped. Exiting loop.")
            break  # Exit the loop

        print(f"Item {item} from class {item_class} priced at {price} has been processed. Status: {row['Status']}")
        





    



from tkinter import Canvas, Scrollbar
import psutil

class TradingApp:
    def __init__(self, master, start_trading_callback, stop_trading_callback, start_auto_chat_callback, stop_auto_chat_callback, monitor_trade_room_callback, stop_monitoring_trade_room_callback, toggle_debug_mode_callback, start_multi_sell):
        try:
            
            self.multi_item_positions = []
            self.class_vars = []
            self.selected_class_values = {}
            self.current_status_dict = {}
            
            ## DATA 
            self.successful_sales_var = tk.StringVar(value='Sales: 0')  # Add initial value
            self.total_gold_var = tk.StringVar(value='Gold Earned: 0')  # Add initial value

            ## DATA END
            
            
            self.master = master
            self.start_trading_callback = start_trading_callback
            self.stop_trading_callback = stop_trading_callback
            self.start_auto_chat_callback = start_auto_chat_callback
            self.start_multi_chat_callback = start_multi_sell
            self.stop_auto_chat_callback = stop_auto_chat_callback
            self.monitor_trade_room_callback = monitor_trade_room_callback
            self.stop_monitoring_trade_room_callback = stop_monitoring_trade_room_callback
            self.toggle_debug_mode_callback = toggle_debug_mode_callback

            self.master.title("The Old Trader")
            self.master.geometry("1000x450")
            #self.master.resizable(False, False)


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
            
            

            frame1 = tk.Frame(self.tab_auto_sell, borderwidth=2, relief="groove")

            frame2 = tk.Frame(self.tab_auto_sell, borderwidth=2, relief="groove")
            frame3 = tk.Frame(self.tab_auto_sell)
            
            frame1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            frame2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
            frame3.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
            
            self.tab_auto_sell.grid_columnconfigure(0, weight=1)
            self.tab_auto_sell.grid_columnconfigure(1, weight=1)
            self.tab_auto_sell.grid_columnconfigure(2, weight=3)
            
            
            self.inner_frame = tk.Frame(self.tab_auto_trade)
            #
            self.inner_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            
            
            # Load button for images
            self.load_button = tk.Button(self.master, text="Load Item Image", command=self.load_item_image)
            self.load_button.pack(in_=self.tab_auto_trade, pady=5)

            self.refresh_images()
            
            
            # Customize the font
            custom_font = ("Helvetica", 16, "bold")

            # For frame1
            frame1_header = ttk.Label(frame1, text="Start & Stop", font=custom_font)
            frame1_header.pack(side=tk.TOP, padx=5, pady=5)

            # For frame2
            frame2_header = ttk.Label(frame2, text="Single-Sell", font=custom_font)
            frame2_header.pack(side=tk.TOP, padx=5, pady=5)
            

            
            # For frame3
            frame3_header = ttk.Label(frame3, text="Multi-Sell", font=custom_font, anchor="center", justify="center")
            frame3_header.pack(side=tk.TOP, padx=50, pady=5)
            
            # Create a variable to hold the selected option
            self.sell_option_var = tk.StringVar(value='1')  # Default to 

            # Create the radio buttons

            single_sell_radio = ttk.Radiobutton(frame1, text='Single-Sell', variable=self.sell_option_var, value='1')
            multi_sell_radio = ttk.Radiobutton(frame1, text='Multi-Sell', variable=self.sell_option_var, value='2')
            
            # Place the radio buttons in frame1
            multi_sell_radio.pack(side=tk.TOP, padx=5, pady=5)
            single_sell_radio.pack(side=tk.TOP, padx=5, pady=10)
            


            self.start_chat_button = ttk.Button(
                self.master, 
                text="Start Auto Sell", 
                command=self.start_sell_thread,
                bootstyle='success'
            )
            self.start_chat_button.pack(in_=frame1, pady=5)

            self.stop_chat_button = ttk.Button(self.master, text="Stop Auto Sell", command=self.stop_auto_chat_callback)
            self.stop_chat_button.pack(in_=frame1, pady=5)
            
            # Create the Clear button
            self.clear_button = ttk.Button(
                frame1, 
                text="Clear List", 
                command=self.clear_table,  # Set the command to the function to clear the list and update the table
                bootstyle='danger'
            )
            self.clear_button.pack(in_=frame1, pady=5)

            
            
            self.kill_switch_var = tk.BooleanVar(value=False)
            self.kill_switch_active = False

            self.kill_switch_button = ttk.Checkbutton(
                frame1,
                text="Kill Switch",
                variable=self.kill_switch_var,
                command=self.toggle_kill_switch
            )
            self.kill_switch_button.pack(side=tk.TOP, padx=5, pady=5)

            # Create a frame to hold the entry and label
            self.delay_frame = tk.Frame(frame1)
            self.delay_frame.pack(side=tk.TOP, padx=5, pady=5)

            self.kill_delay_var = tk.StringVar(value="60")  # Default delay is 1 minute
            self.kill_delay_entry = ttk.Entry(self.delay_frame, textvariable=self.kill_delay_var, state="disabled", width=5)
            self.kill_delay_entry.pack(side=tk.LEFT)

            self.min_label = tk.Label(self.delay_frame, text="min")
            self.min_label.pack(side=tk.LEFT)
            
            
            
            keybind_info = (
                "SHIFT: Capture Item Position\n"
                "F8: Stop Auto Selling/Trading\n"
            )
            keybind_text = tk.Text(self.tab_auto_sell, height=4, width=30, wrap=tk.WORD, relief=tk.GROOVE)
            keybind_text.insert(tk.END, keybind_info)
            keybind_text.config(state=tk.DISABLED)  # Make it read-only
            keybind_text.pack(in_=frame1, padx=5, pady=50)
        

            # Place the notebook on the Tkinter window
            self.notebook.pack(expand=True, fill='both')
            

            self.start_button = ttk.Button(self.master, text="Start Trading", command=lambda: threading.Thread(target=self.start_trading_callback).start())
            self.start_button.pack(in_=self.tab_auto_trade, pady=5)

            self.stop_button = ttk.Button(self.master, text="Stop Trading", command=self.stop_trading_callback)
            self.stop_button.pack(in_=self.tab_auto_trade, pady=5)
            
            self.chat_label = Label(root, text="Sell Price:")
            self.chat_label.pack(in_=frame2, pady=(20,5))

            # Entry box for chat text
            self.chat_entry = ttk.Entry(root, validate="key", validatecommand=(validate_cmd, '%P'), width=30, bootstyle='success')
            self.chat_entry.pack(in_=frame2, pady=5)
            self.chat_entry.insert(0, "100")  # Default text

            #keyboard.add_hotkey('F7', start_auto_chat, args=(self.chat_entry,))
            
            
            
            frame2_counters = ttk.Frame(frame2)
            frame2_counters.pack(pady=(20, 5))
            
            self.successful_sales_label = Label(self.tab_auto_sell, textvariable=self.successful_sales_var)
            self.successful_sales_label.pack(in_=frame2, pady=(10, 5))

            self.total_gold_label = Label(self.tab_auto_sell, textvariable=self.total_gold_var)
            self.total_gold_label.pack(in_=frame2, pady=(10, 5))
            
            ## TABLE ##
            
            # Create canvas and scrollbar
            self.canvas = tk.Canvas(frame3, height=int(frame3.winfo_height() * 0.6))
            scrollbar = ttk.Scrollbar(frame3, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=scrollbar.set)

            scrollbar.pack(side="right", fill="y")
            self.canvas.pack(side="left", fill="both", expand=True)

            self.table_frame = tk.Frame(self.canvas)
            self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")

            self.table_frame.update_idletasks()
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
            
            
            # Add table headers
            tk.Label(self.table_frame, text="Item", width=16, borderwidth=1, relief="solid").grid(row=0, column=0)
            tk.Label(self.table_frame, text="Class", width=16, borderwidth=1, relief="solid").grid(row=0, column=1)
            tk.Label(self.table_frame, text="Price", width=16, borderwidth=1, relief="solid").grid(row=0, column=2)
            tk.Label(self.table_frame, text="Status", width=16, borderwidth=1, relief="solid").grid(row=0, column=3)
            
            # Sample data for the table
            data = [
                {"Item": "Apple", "Class": "Ranger", "Price": 50, "Status": "Sold"},
                {"Item": "Apple", "Class": "Ranger", "Price": 50, "Status": "Selling"},
                # ... add more items here
            ]
            


            # Loop through rows to create table widgets
            for i, row_data in enumerate(self.multi_item_positions, start=1):
                tk.Label(self.table_frame, text=row_data["Item"], width=20, borderwidth=2, relief="solid").grid(row=i, column=0)

                # Dropdown menu for 'Class' column
                class_var = tk.StringVar(value=row_data["Class"])
                self.class_vars.append(class_var)
                
                class_menu = ttk.OptionMenu(self.table_frame, class_var, row_data["Class"], *class_list)

                class_menu.grid(row=i, column=1)
                class_var.trace_add('write', lambda *args, i=i: self.update_row_value(i, 'Class', class_var))

                # Editable entry for 'Price' column
                price_var = tk.StringVar(value=row_data["Price"])
                price_entry = tk.Entry(self.table_frame, width=10, textvariable=price_var)
                price_entry.grid(row=i, column=2)
                price_var.trace_add('write', lambda *args, i=i: self.update_row_value(i, 'Price', price_var))

                tk.Label(self.table_frame, text=row_data["Status"], width=10, borderwidth=1, relief="solid").grid(row=i, column=3)
            
            self.table_frame.update_idletasks()
            #canvas.config(scrollregion=canvas.bbox("all"))


            self.test_button = ttk.Button(self.master, text="Test Trade Room", command=lambda: threading.Thread(target=self.monitor_trade_room_callback).start())
            self.test_button.pack(in_=self.tab_development, pady=5)

            self.stop_monitor_button = ttk.Button(self.master, text="Stop Monitoring Trade Room", command=self.stop_monitoring_trade_room_callback)
            self.stop_monitor_button.pack(in_=self.tab_development, pady=5)

            self.debug_button = ttk.Button(self.master, text="Toggle Debug", command=self.toggle_debug_mode_callback)
            self.debug_button.pack(in_=self.tab_development, pady=5)
            
            

        except Exception as e:
            print(e)
            
    def start_sell_thread(self):
        if self.sell_option_var.get() == '1':
            threading.Thread(target=self.start_auto_chat_callback, args=(self.chat_entry,)).start()
        else:
            threading.Thread(target=self.start_multi_chat_callback, args=(self.multi_item_positions,)).start()


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
        
        
        # Create a method to update the UI
    def update_ui(self, successful_sales, total_gold):
        self.successful_sales_var.set(f"Sales: {successful_sales}")
        self.total_gold_var.set(f"Gold Earned: {total_gold}")

    def update_table(self):
        print("Updating table...")
        #print(f"Data: {self.multi_item_positions}")

        # Clear existing widgets in the table frame
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Recreate headers
        tk.Label(self.table_frame, text="Item", width=16, borderwidth=1, relief="solid").grid(row=0, column=0)
        tk.Label(self.table_frame, text="Class", width=16, borderwidth=1, relief="solid").grid(row=0, column=1)
        tk.Label(self.table_frame, text="Price", width=16, borderwidth=1, relief="solid").grid(row=0, column=2)
        tk.Label(self.table_frame, text="Status", width=16, borderwidth=1, relief="solid").grid(row=0, column=3)

        # Recreate the table
        for i, row_data in enumerate(self.multi_item_positions, start=1):
            print(f"Adding row {i} with data {row_data}")
            
            tk.Label(self.table_frame, text=row_data["Item"], width=16, borderwidth=1, relief="solid").grid(row=i, column=0)


            # Dropdown for 'Class' column
            class_var = tk.StringVar()  # Create the StringVar without an initial value

            # Set the selected option based on row_data["Class"]
            class_var.set(row_data["Class"])

            class_menu = ttk.OptionMenu(self.table_frame, class_var, row_data["Class"], *class_list)
            class_menu.grid(row=i, column=1, padx=5, pady=5)

            # Use row_data["RowId"] directly
            class_var.trace_add('write', lambda *args, class_var=class_var, row_data=row_data: self.update_row_value(row_data["RowId"], 'Class', class_var))

            # Editable entry for 'Price' column
            price_var = tk.StringVar(value=row_data["Price"])
            price_entry = tk.Entry(self.table_frame, width=15, textvariable=price_var)
            price_entry.grid(row=i, column=2)

            # Use row_data["RowId"] directly
            price_var.trace_add('write', lambda *args, price_var=price_var, row_data=row_data: self.update_row_value(row_data["RowId"], 'Price', price_var))

            tk.Label(self.table_frame, text=row_data["Status"], width=16, borderwidth=1, relief="solid").grid(row=i, column=3)
            

        # Update the canvas scroll region
        self.table_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        print("Table updated.")



    def clear_table(self):
        self.multi_item_positions.clear()  # Clear the list
        self.update_table()  # Update the table to reflect the changes
        print("Table cleared.")


    # A function to update the class and price when changed
    def update_row_value(self, row_id, key, var):
        new_value = var.get()
        for i, row_data in enumerate(self.multi_item_positions):
            if row_data["RowId"] == row_id:
                row_data[key] = new_value
                #print(f"Updated row {i + 1}, {key} to {new_value}")
                #print(f"Current state of multi_item_positions: {self.multi_item_positions}")
                break  # Exit the loop once the row is found
            
            
    def toggle_kill_switch(self):
        self.kill_switch_active = self.kill_switch_var.get()
        if self.kill_switch_active:
            self.kill_delay_entry.config(state="normal")
            delay = int(self.kill_delay_var.get()) * 60  # Convert minutes to seconds
            threading.Thread(target=self.kill_process_and_script, args=(delay,)).start()
        else:
            self.kill_delay_entry.config(state="disabled")

    def kill_process_and_script(self, delay):
        start_time = time.time()
        
        while time.time() - start_time < delay:
            time.sleep(1)
            if not self.kill_switch_active:
                print("Kill switch deactivated.")
                return
        
        print("Kill switch activated.")

        # Kill the game process (replace "GameExecutable.exe" with your game's executable name)
        for proc in psutil.process_iter(attrs=["pid", "name"]):
            if "DungeonCrawler.exe" in proc.info["name"]:
                psutil.Process(proc.info["pid"]).terminate()

        # Kill the script
        os._exit(0)


app = TradingApp(
    root, 
    start_trading, 
    stop_trading, 
    start_auto_chat, 
    stop_auto_chat, 
    monitor_trade_room, 
    stop_monitoring_trade_room,
    toggle_debug_mode,
    start_multi_sell,
)

# Keybinding to capture item positions
keyboard.on_press_key('shift', lambda e, app=app: capture_item_position(app, e), suppress=False)

icon = './icons/gold.png'
from tkinter import PhotoImage

root.iconphoto(True, PhotoImage(file=icon))

root.after(1000, app.update_table) # Update the table every second
root.after(100, check_queue)
root.mainloop()