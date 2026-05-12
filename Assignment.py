import string
import time

class Item:
    """The <<Entity>> class representing the object being sorted."""
    def __init__(self, item_id: int, color: string, weight: float):
        self.id = item_id
        self.color = color
        self.weight = weight

    def getProperties(self):
        return {"id": self.id, "color": self.color, "weight": self.weight}

class SensorArray:
    """The input interface for scanning items."""
    def __init__(self):
        self.sensor_status = True

    def scanItem(self, item: Item):
        if self.validateReadings(item):
            print(f"[Sensor] Scanned Item {item.id}: Color={item.color}, Weight={item.weight}kg")
            return item
        return None

    def validateReadings(self, item: Item):
        # Basic validation: check if data is within expected ranges
        return item.weight > 0 and isinstance(item.color, str)

class ActuatorSystem:
    """The output interface for physical movement."""
    def __init__(self):
        self.current_bin_id = 0
        self.is_operational = True

    def move_to_bin(self, bin_id: int):
        self.current_bin_id = bin_id
        print(f"[Actuator] Moving arm to Bin {bin_id}...")
        time.sleep(0.5) # Simulating mechanical movement
        print(f"[Actuator] Item sorted into Bin {bin_id}.")

    def resetPosition(self):
        self.current_bin_id = 0
        print("[Actuator] Resetting to home position.")

class SortingController:
    """The central 'Brain' that coordinates the sensors and actuators."""
    def __init__(self, threshold: float):
        self.weight_threshold = threshold
        self.operation_log = []
        self.sensors = SensorArray()
        self.actuators = ActuatorSystem()

    def calculate_logic(self, item: Item) -> int:
        """The Decision Matrix: Weight takes priority, then Color."""
        if item.weight >= self.weight_threshold:
            return 1  # Heavy Items Bin
        
        # Color-based logic for lighter items
        color_map = {"red": 2, "blue": 3, "green": 4}
        return color_map.get(item.color.lower(), 5) # 5 is the 'Other' bin

    def process_cycle(self, item: Item):
        print(f"\n--- Starting Cycle for Item {item.id} ---")
        
        # 1. Scan
        scanned_item = self.sensors.scanItem(item)
        
        if scanned_item:
            # 2. Decide
            target_bin = self.calculate_logic(scanned_item)
            
            # 3. Actuate
            self.actuators.move_to_bin(target_bin)
            
            # 4. Log
            log_entry = f"Item {item.id}: Bin {target_bin}"
            self.operation_log.append(log_entry)
            
            self.actuators.resetPosition()
        else:
            print("[Error] Invalid Sensor Readings. Cycle Aborted.")

# --- Demo/Execution ---
if __name__ == "__main__":
    # Create the controller with a 2.0kg threshold
    controller = SortingController(threshold=2.0)
    
    # Simulate a batch of items
    batch = [
        Item(101, "Red", 2.5),  # Heavy
        Item(102, "Blue", 0.5), # Light Blue
        Item(103, "Yellow", 1.2) # Other
    ]
    
    for obj in batch:
        controller.process_cycle(obj)
    
    print("\n[Final Report] Operation Log:", controller.operation_log)