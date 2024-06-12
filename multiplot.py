import os
import time
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import ttk

# Global dictionaries to hold data for each file
file_data = {
    "data.bak": {"times": [], "currents": [], "voltages": [], "last_line_read": 0},
    "data1.bak": {"times": [], "currents": [], "voltages": [], "last_line_read": 0},
    "data2.bak": {"times": [], "currents": [], "voltages": [], "last_line_read": 0},
    "data3.bak": {"times": [], "currents": [], "voltages": [], "last_line_read": 0},
}

def read_data(filename):
    """
    Reads data from the specified file and updates global lists with new data.
    """
    try:
        with open(filename, "r") as f:
            lines = f.readlines()
            if not lines:
                print("Warning: Empty file.")
                return

            # Process only new lines
            last_line_read = file_data[filename]["last_line_read"]
            new_lines = lines[last_line_read:]
            for line in new_lines:
                time_interval, current, voltage = line.strip().split(",")
                file_data[filename]["times"].append(float(time_interval))
                file_data[filename]["currents"].append(float(current))
                file_data[filename]["voltages"].append(float(voltage))
            
            # Update the last line read index
            file_data[filename]["last_line_read"] = len(lines)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error reading data: {e}")

def update_plot(filename, figure, canvas):
    """
    Updates the Matplotlib plot with the new data.
    """
    times = file_data[filename]["times"]
    currents = file_data[filename]["currents"]
    voltages = file_data[filename]["voltages"]

    plt.figure(figure.number)
    plt.clf()
    plt.plot(times, currents, label='Current (A)', color='blue')
    plt.plot(times, voltages, label='Voltage (V)', color='red')
    plt.xlabel('Time (s)')
    plt.ylabel('Values')
    plt.title(f'Real-time Data Plot - {filename}')
    plt.legend()
    plt.grid(True)
    canvas.draw()

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, filename, root, figure, canvas):
        self.filename = filename
        self.root = root
        self.figure = figure
        self.canvas = canvas

    def on_modified(self, event):
        if event.src_path.endswith(self.filename):
            read_data(self.filename)
            self.root.after(1, update_plot, self.filename, self.figure, self.canvas)

def monitor_file(filename, root, figure, canvas):
    """
    Monitors the specified file for changes and updates the Matplotlib plot.
    """
    event_handler = FileChangeHandler(filename, root, figure, canvas)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer_thread = threading.Thread(target=observer.start)
    observer_thread.daemon = True
    observer_thread.start()

def create_plot_window(filename):
    window = tk.Toplevel()
    window.title(f"Plot - {filename}")

    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Initialize plot with existing data
    read_data(filename)
    update_plot(filename, fig, canvas)
    
    monitor_file(filename, window, fig, canvas)

def create_main_window():
    root = tk.Tk()
    root.title("Data Plotter")

    # Buttons to open individual plot windows
    for filename in file_data.keys():
        btn = ttk.Button(root, text=f"Open {filename} Plot", command=lambda fn=filename: create_plot_window(fn))
        btn.pack(pady=5)

    # Button to open grid view window
    grid_btn = ttk.Button(root, text="Open Grid View", command=create_grid_view_window)
    grid_btn.pack(pady=5)

    root.mainloop()

def create_grid_view_window():
    grid_window = tk.Toplevel()
    grid_window.title("Grid View")

    fig, axs = plt.subplots(2, 2, figsize=(10, 10))
    axs = axs.flatten()

    for ax, (filename, data) in zip(axs, file_data.items()):
        read_data(filename)
        ax.plot(data["times"], data["currents"], label='Current (A)', color='blue')
        ax.plot(data["times"], data["voltages"], label='Voltage (V)', color='red')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Values')
        ax.set_title(f'{filename}')
        ax.legend()
        ax.grid(True)

    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=grid_window)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()

if __name__ == "__main__":
    create_main_window()
