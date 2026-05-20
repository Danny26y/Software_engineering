import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading


class Item:
    """The <<Entity>> class representing the object being sorted."""

    def __init__(self, item_id: int, color: str, weight: float):
        self.id = item_id
        self.color = color
        self.weight = weight

    def getProperties(self):
        return {"id": self.id, "color": self.color, "weight": self.weight}


class SensorArray:
    """The input interface for scanning items."""

    def __init__(self):
        self.sensor_status = True

    def scanItem(self, item: Item, log_callback):
        if self.validateReadings(item):
            log_callback(f"[Sensor] Scanned Item {item.id}: Color={item.color}, Weight={item.weight}kg")
            return item
        return None

    def validateReadings(self, item: Item):
        return item.weight > 0 and isinstance(item.color, str)


class ActuatorSystem:
    """The output interface for physical movement."""

    def __init__(self):
        self.current_bin_id = 0
        self.is_operational = True

    def move_to_bin(self, bin_id: int, log_callback, gui_update_callback):
        self.current_bin_id = bin_id
        log_callback(f"[Actuator] Moving arm to Bin {bin_id}...")

        # Highlight the active sorting bin in the UI
        gui_update_callback(bin_id, "active")
        time.sleep(0.8)  # Simulated mechanical latency

        log_callback(f"[Actuator] Item sorted into Bin {bin_id}.")
        gui_update_callback(bin_id, "sorted")

    def resetPosition(self, log_callback):
        self.current_bin_id = 0
        log_callback("[Actuator] Resetting to home position.")


class SortingController:
    """The central 'Brain' that coordinates system layers and updates the GUI."""

    def __init__(self, threshold: float, log_callback, gui_update_callback):
        self.weight_threshold = threshold
        self.operation_log = []
        self.sensors = SensorArray()
        self.actuators = ActuatorSystem()
        self.log_callback = log_callback
        self.gui_update_callback = gui_update_callback

    def calculate_logic(self, item: Item) -> int:
        if item.weight >= self.weight_threshold:
            return 1  # Heavy Items Bin

        color_map = {"red": 2, "blue": 3, "green": 4}
        return color_map.get(item.color.lower(), 5)  # 5 is the 'Other' bin

    def process_cycle(self, item: Item):
        self.log_callback(f"\n--- Starting Cycle for Item {item.id} ---")

        scanned_item = self.sensors.scanItem(item, self.log_callback)

        if scanned_item:
            target_bin = self.calculate_logic(scanned_item)
            self.actuators.move_to_bin(target_bin, self.log_callback, self.gui_update_callback)

            log_entry = f"Item {item.id}: Bin {target_bin}"
            self.operation_log.append(log_entry)

            time.sleep(0.4)
            self.actuators.resetPosition(self.log_callback)
        else:
            self.log_callback("[Error] Invalid Sensor Readings. Cycle Aborted.")


# --- GUI Layer ---
class SortingSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Group 10 - Automated Mechatronic Sorting System Panel")
        self.root.geometry("850x600")
        self.root.configure(bg="#f4f6f9")

        # Initialize default controller
        self.controller = SortingController(threshold=2.0, log_callback=self.write_to_console,
                                            gui_update_callback=self.update_bin_visual)
        self.item_counter = 101

        self.setup_ui()

    def setup_ui(self):
        # Title Header
        header = tk.Label(self.root, text="Warehouse Sorting Control Interface (Digital Twin)",
                          font=("Helvetica", 16, "bold"), bg="#1e293b", fg="white", pady=10)
        header.pack(fill=tk.X)

        # Main Layout Split (Left Control Panel, Right Bin Visuals)
        main_frame = tk.Frame(self.root, bg="#f4f6f9")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        left_panel = tk.Frame(main_frame, bg="#f4f6f9", width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=10)

        right_panel = tk.Frame(main_frame, bg="#ffffff", bd=1, relief=tk.SOLID)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=15, pady=15)

        # --- Left Panel: Inputs & Controls ---
        input_group = tk.LabelFrame(left_panel, text=" Manual Entry Scanner Input ", font=("Helvetica", 10, "bold"),
                                    padx=10, pady=10, bg="#f4f6f9")
        input_group.pack(fill=tk.X, pady=5)

        tk.Label(input_group, text="Item Color:", bg="#f4f6f9").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.color_var = tk.StringVar(value="Red")
        color_menu = ttk.Combobox(input_group, textvariable=self.color_var,
                                  values=["Red", "Blue", "Green", "Yellow", "Orange"], state="readonly")
        color_menu.grid(row=0, column=1, sticky="ew", pady=4)  # Fixed fill -> sticky

        tk.Label(input_group, text="Weight (kg):", bg="#f4f6f9").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.weight_entry = ttk.Entry(input_group)
        self.weight_entry.insert(0, "1.5")
        self.weight_entry.grid(row=1, column=1, sticky="ew", pady=4)  # Fixed fill -> sticky

        # Configure columns inside input_group so sticky="ew" knows what space to fill
        input_group.grid_columnconfigure(1, weight=1)

        btn_process = ttk.Button(input_group, text="Feed Item to Conveyor", command=self.submit_single_item)
        btn_process.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

        # Preset Batch Control
        batch_group = tk.LabelFrame(left_panel, text=" Automation Run Controls ", font=("Helvetica", 10, "bold"),
                                    padx=10, pady=10, bg="#f4f6f9")
        batch_group.pack(fill=tk.X, pady=10)

        btn_batch = ttk.Button(batch_group, text="Run Default Demo Batch (3 Items)", command=self.run_demo_batch)
        btn_batch.pack(fill=tk.X, pady=4)

        # System Log / Terminal Output
        log_group = tk.LabelFrame(left_panel, text=" Real-Time Telemetry Logs ", font=("Helvetica", 10, "bold"),
                                  bg="#f4f6f9")
        log_group.pack(fill=tk.BOTH, expand=True, pady=5)

        self.txt_console = tk.Text(log_group, height=15, width=40, font=("Courier New", 9), bg="#0f172a", fg="#38bdf8")
        self.txt_console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- Right Panel: Physical Bin Representation ---
        tk.Label(right_panel, text="Actuator Arm Destination Sorting Bins", font=("Helvetica", 12, "bold"), bg="white",
                 fg="#334155").pack(anchor=tk.W, pady=5)

        self.bin_widgets = {}
        bins_definition = [
            (1, "Bin 1: Heavy Items (≥2.0kg)"),
            (2, "Bin 2: Light Red Items"),
            (3, "Bin 3: Light Blue Items"),
            (4, "Bin 4: Light Green Items"),
            (5, "Bin 5: Other / Unknown Catch-All")
        ]

        for bin_id, label in bins_definition:
            frame = tk.Frame(right_panel, bg="#f1f5f9", bd=1, relief=tk.GROOVE, pady=10, padx=10)
            frame.pack(fill=tk.X, pady=4)

            indicator = tk.Label(frame, text="IDLE", font=("Helvetica", 9, "bold"), bg="#64748b", fg="white", width=10)
            indicator.pack(side=tk.LEFT)

            txt_label = tk.Label(frame, text=label, font=("Helvetica", 10), bg="#f1f5f9", padx=10)
            txt_label.pack(side=tk.LEFT)

            self.bin_widgets[bin_id] = {"frame": frame, "indicator": indicator}

            indicator = tk.Label(frame, text="IDLE", font=("Helvetica", 9, "bold"), bg="#64748b", fg="white", width=10)
            indicator.pack(side=tk.LEFT)

            txt_label = tk.Label(frame, text=label, font=("Helvetica", 10), bg="#f1f5f9", padx=10)
            txt_label.pack(side=tk.LEFT)

            self.bin_widgets[bin_id] = {"frame": frame, "indicator": indicator}

    def write_to_console(self, msg):
        self.txt_console.insert(tk.END, msg + "\n")
        self.txt_console.see(tk.END)

    def update_bin_visual(self, bin_id, state):
        # Ensure changes happen safely on main UI event thread
        def ui_action():
            if state == "active":
                self.bin_widgets[bin_id]["frame"].configure(bg="#ffe4e6")
                self.bin_widgets[bin_id]["indicator"].configure(text="ROUTING...", bg="#f43f5e")
            elif state == "sorted":
                self.bin_widgets[bin_id]["frame"].configure(bg="#dcfce7")
                self.bin_widgets[bin_id]["indicator"].configure(text="ITEM SORTED", bg="#22c55e")
                # Reset highlight color cleanly after a brief moment
                self.root.after(1500, lambda: self.reset_bin_ui(bin_id))

        self.root.after(0, ui_action)

    def reset_bin_ui(self, bin_id):
        self.bin_widgets[bin_id]["frame"].configure(bg="#f1f5f9")
        self.bin_widgets[bin_id]["indicator"].configure(text="IDLE", bg="#64748b")

    def submit_single_item(self):
        try:
            weight = float(self.weight_entry.get())
            color = self.color_var.get()

            item = Item(self.item_counter, color, weight)
            self.item_counter += 1

            # Execute cycle on background thread to prevent UI freezing during time.sleep() delays
            threading.Thread(target=self.controller.process_cycle, args=(item,), daemon=True).start()
        except ValueError:
            messagebox.showerror("Sensor Parsing Fault",
                                 "Please enter a valid weight parameter (numeric float fraction).")

    def run_demo_batch(self):
        def run():
            batch = [
                Item(201, "Red", 2.5),
                Item(202, "Blue", 0.5),
                Item(203, "Yellow", 1.2)
            ]
            for obj in batch:
                self.controller.process_cycle(obj)
                time.sleep(1.0)  # Break spacing between batch operations

        threading.Thread(target=run, daemon=True).start()


if __name__ == "__main__":
    window = tk.Tk()
    app = SortingSystemGUI(window)
    window.mainloop()