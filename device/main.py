import tkinter as tk
from tkinter import messagebox
import numpy as np
import os
import threading
import joblib
import pandas as pd
import logging
from PIL import Image, ImageTk
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor, XGBClassifier
import random  # Import random to simulate sensor readings
import websocket
import json

# Global WebSocket instance
ws = None
ws_lock = threading.Lock()  # Lock for thread safety

# Set up logging
logging.basicConfig(filename='soil_quality_analysis.log', level=logging.INFO)


def on_message(ws, message):
    # Parse the incoming message
    data = json.loads(message)
    print(data)
    # Example: run collect or predict based on the message content
    if data.get("event") == "client-collect":
        collect_data_in_background()
    elif data.get("event") == "client-predict":
        predict_sqi_and_fertilizer()


def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws):
    print("WebSocket closed")

def on_open(ws):
    print("WebSocket connection opened")
    # Send a message to identify as a device
    connection_data = {
        "event": "connection",
        "data": {"type": "device"}
    }
    ws.send(json.dumps(connection_data))

def listen_for_websocket_messages():
    global ws  # Use the global WebSocket instance
    websocket.enableTrace(True)
    
    # Initialize the WebSocketApp
    ws = websocket.WebSocketApp("ws://192.168.1.5:5861", 
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close,
                                  on_open=on_open)

    # Run the WebSocket client forever
    ws.run_forever()

# Start the WebSocket listener in a separate thread
def start_websocket_listener():
    ws_thread = threading.Thread(target=listen_for_websocket_messages)
    ws_thread.daemon = True  # Daemonize thread
    ws_thread.start()

# Function to send data via WebSocket
def send_data_via_websocket(data):
    global ws  # Use the global WebSocket instance
    try:
        # Use lock to ensure thread-safe access
        with ws_lock:
            if ws:
                ws.send(json.dumps(data))
    except Exception as e:
        print(f"Error in WebSocket communication: {e}")


# Set the correct directory where the files are located
BASE_DIR = '/home/RPI4/Desktop/Crop'

# Load models and scaler using joblib
def load_joblib_file(filename):
    try:
        return joblib.load(filename)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

# Load models and scaler
sqi_model = load_joblib_file(os.path.join(BASE_DIR, 'svr_model.joblib'))
suitability_model = load_joblib_file(os.path.join(BASE_DIR, 'svc_model.joblib'))
scaler = load_joblib_file(os.path.join(BASE_DIR, 'scaler(2).joblib'))

# Calibration factors
CALIBRATION_FACTORS = {
    "Nitrogen": 1.05,
    "Phosphorus": 0.95,
    "Potassium": 1.00,
    "Temperature": 1.02,
    "Humidity": 1.00,
    "pH": 0.95  # Example calibration value for pH
}

# Define optimal ranges for each parameter
optimal_ranges = {
    "Nitrogen": (90, 115),
    "Phosphorus": (60, 90),
    "Potassium": (50, 60),
    "Temperature": (21, 37),
    "Humidity": (60, 89),
    "pH": (5.5, 6.5)
}

# Define the function to collect data from RS-485 sensor (simulated)
def collect_data_in_background():
    # Simulate sensor readings
    simulated_readings = {
        "Nitrogen": round(random.uniform(85, 120), 2),
        "Phosphorus": round(random.uniform(60, 90), 2),
        "Potassium": round(random.uniform(40, 60), 2),
        "Temperature": round(random.uniform(21, 37), 2),
        "Humidity": round(random.uniform(60, 90), 2),
        "pH": round(random.uniform(5.5, 6.5), 2)
    }

    # Prepare the data to send
    data_to_send = {
        "event": "device-collect",
        "data": simulated_readings  # Include the simulated readings here
    }

    # Send the data via WebSocket
    send_data_via_websocket(data_to_send)  # Pass the dictionary directly

    # Update the entry fields with simulated readings
    for param, value in simulated_readings.items():
        entry_dict[param].delete(0, tk.END)  # Clear the existing value
        entry_dict[param].insert(0, str(value))  # Insert the simulated value

    messagebox.showinfo("Data Collection", "Simulated sensor readings collected.")

# Function to compare input data with optimal ranges and provide numerical suggestions
def compare_with_reference(features):
    suggestions = []
    param_names = ["Nitrogen", "Phosphorus", "Potassium", "Temperature", "Humidity", "pH"]
    
    for param, value in zip(param_names, features):
        lower_bound, upper_bound = optimal_ranges[param]
        
        if value < lower_bound:
            diff = lower_bound - value
            suggestions.append(f"Increase {param} by {diff:.1f}.")
        elif value > upper_bound:
            diff = value - upper_bound
            suggestions.append(f"Decrease {param} by {diff:.1f}.")
        else:
            suggestions.append(f"{param} is optimal.")

    return "\n".join(suggestions)

# Define the function to predict SQI and suitability
def predict_sqi_and_fertilizer():
    try:
        # Retrieve input values from the Tkinter entry fields
        n = float(entry_dict["Nitrogen"].get())
        p = float(entry_dict["Phosphorus"].get())
        k = float(entry_dict["Potassium"].get())
        temp = float(entry_dict["Temperature"].get())
        humid = float(entry_dict["Humidity"].get())
        ph = float(entry_dict["pH"].get())

        # Prepare the input data and scale it
        new_data = np.array([[n, p, k, temp, humid, ph]])
        new_data_scaled = scaler.transform(new_data)

        # Predict SQI and Remark
        sqi_prediction = sqi_model.predict(new_data_scaled)
        remark_prediction = suitability_model.predict(new_data_scaled)

        # Interpret SQI
        sqi_value = sqi_prediction[0]
        suitability, reason = interpret_sqi(sqi_value, [n, p, k, temp, humid, ph])

        # Compare with reference data and get suggestions
        comparison_suggestions = compare_with_reference([n, p, k, temp, humid, ph])

        # Show the results in a message box
        result_text = (f"Predicted SQI: {sqi_value:.2f}\n"
                       f"Predicted Remark: {remark_prediction[0]}\n\n"
                       f"Reason: {reason}\n\n"
                       f"Comparative Analysis:\n{comparison_suggestions}")

        messagebox.showinfo("Result", result_text)
    
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid numbers for all fields.")

# Define a function to interpret SQI and provide explanations
def interpret_sqi(sqi, features):
    n, p, k, temp, humid, ph = features

    if sqi < 0.3:
        suitability = "Low Suitability"
        reason = (
            f"Low SQI indicates significant issues:\n"
            f"- Nitrogen, Phosphorus, Potassium, Temperature, Humidity, or pH may be suboptimal."
        )
    elif 0.3 <= sqi < 0.5:
        suitability = "Moderate Suitability"
        reason = (
            f"- Conditions are okay but optimizing some parameters may help."
        )
    elif sqi >= 0.5:
        suitability = "High Suitability"
        reason = (
            f"High SQI indicates optimal conditions:\n"
            f"- All parameters are within ideal ranges."
        )

    return suitability, reason


# Adjust font size and window based on screen size
def adjust_for_screen(screen_mode):
    if screen_mode == 'TV':
        font_style = ("Helvetica", 20)
        btn_font_style = ("Helvetica", 18, "bold")
        label_font = ("Helvetica", 18)
    elif screen_mode == 'LCD':
        font_style = ("Helvetica", 9)
        btn_font_style = ("Helvetica", 9, "bold")
        label_font = ("Helvetica", 9)
    else:
        font_style = ("Helvetica", 9)
        btn_font_style = ("Helvetica", 9, "bold")
        label_font = ("Helvetica", 9)
    
    return font_style, btn_font_style, label_font

# Create the GUI window
root = tk.Tk()
root.title("Soil Quality Analysis Tool")

# Set the window to full screen
root.attributes("-fullscreen", True)

# Get the current directory (where your main.py is located)
current_directory = os.path.dirname(os.path.abspath(__file__))

# Define the background image path (in the same folder as main.py)
bg_image_path = os.path.join(current_directory, 'background.jpg')

# Open the background image
bg_image = Image.open(bg_image_path)

# Resize the background image to fit the window size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
bg_image = bg_image.resize((screen_width, screen_height), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

# Set the background label to display the image
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Select the screen mode ('TV' or 'LCD')
screen_mode = 'TV'  # Change this to 'LCD' for 5-inch LCD screen mode

font_style, btn_font_style, label_font = adjust_for_screen(screen_mode)

frame = tk.Frame(root)
frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Inputs and labels for features
inputs = ["Nitrogen", "Phosphorus", "Potassium", "Temperature", "Humidity", "pH"]
entry_dict = {}

for idx, label_text in enumerate(inputs):
    label = tk.Label(frame, text=label_text, font=label_font)
    label.grid(row=idx, column=0, padx=10, pady=5)
    
    entry = tk.Entry(frame, font=label_font, width=10)
    entry.grid(row=idx, column=1, padx=10, pady=5)
    entry_dict[label_text] = entry

# Buttons
collect_button = tk.Button(frame, text="Collect Data", command=collect_data_in_background, font=btn_font_style)
collect_button.grid(row=len(inputs), column=0, columnspan=2, pady=20)

predict_button = tk.Button(frame, text="Predict", command=predict_sqi_and_fertilizer, font=btn_font_style)
predict_button.grid(row=len(inputs) + 1, column=0, columnspan=2, pady=20)

exit_button = tk.Button(frame, text="Exit", command=root.quit, font=btn_font_style)
exit_button.grid(row=len(inputs) + 2, column=0, columnspan=2, pady=20)

start_websocket_listener()

root.mainloop()
