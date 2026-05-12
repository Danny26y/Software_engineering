import unittest
from unittest.mock import patch, MagicMock
import io

# ── fix the `string` type annotation bug before importing ──────────────────
import builtins, sys
builtins.string = str          # patch so the class definition doesn't crash

# paste / import the module under test
# (assuming it lives in sorting_system.py; adjust as needed)
from Assignment import Item, SensorArray, ActuatorSystem, SortingController


class TestItem(unittest.TestCase):

    def test_creation(self):
        item = Item(1, "red", 1.5)
        self.assertEqual(item.id, 1)
        self.assertEqual(item.color, "red")
        self.assertEqual(item.weight, 1.5)

    def test_get_properties(self):
        item = Item(42, "blue", 3.0)
        props = item.getProperties()
        self.assertEqual(props, {"id": 42, "color": "blue", "weight": 3.0})


class TestSensorArray(unittest.TestCase):

    def setUp(self):
        self.sensor = SensorArray()

    def test_initial_status(self):
        self.assertTrue(self.sensor.sensor_status)

    def test_valid_scan_returns_item(self):
        item = Item(1, "green", 1.0)
        result = self.sensor.scanItem(item)
        self.assertIs(result, item)

    def test_invalid_weight_returns_none(self):
        item = Item(2, "red", -1.0)          # negative weight → invalid
        result = self.sensor.scanItem(item)
        self.assertIsNone(result)

    def test_zero_weight_returns_none(self):
        item = Item(3, "red", 0)
        result = self.sensor.scanItem(item)
        self.assertIsNone(result)

    def test_validate_readings_true(self):
        item = Item(4, "blue", 0.1)
        self.assertTrue(self.sensor.validateReadings(item))

    def test_validate_readings_false_bad_weight(self):
        item = Item(5, "blue", 0)
        self.assertFalse(self.sensor.validateReadings(item))


class TestActuatorSystem(unittest.TestCase):

    def setUp(self):
        self.actuator = ActuatorSystem()

    def test_initial_state(self):
        self.assertEqual(self.actuator.current_bin_id, 0)
        self.assertTrue(self.actuator.is_operational)

    @patch("time.sleep")                       # skip the 0.5 s delay
    def test_move_to_bin_updates_id(self, _mock_sleep):
        self.actuator.move_to_bin(3)
        self.assertEqual(self.actuator.current_bin_id, 3)

    @patch("time.sleep")
    def test_reset_position(self, _mock_sleep):
        self.actuator.move_to_bin(2)
        self.actuator.resetPosition()
        self.assertEqual(self.actuator.current_bin_id, 0)


class TestSortingController(unittest.TestCase):

    def setUp(self):
        self.controller = SortingController(threshold=2.0)

    # ── calculate_logic ────────────────────────────────────────────────────

    def test_heavy_item_goes_to_bin_1(self):
        item = Item(1, "red", 2.5)
        self.assertEqual(self.controller.calculate_logic(item), 1)

    def test_threshold_boundary_goes_to_bin_1(self):
        item = Item(2, "blue", 2.0)           # exactly at threshold → bin 1
        self.assertEqual(self.controller.calculate_logic(item), 1)

    def test_light_red_goes_to_bin_2(self):
        item = Item(3, "red", 1.0)
        self.assertEqual(self.controller.calculate_logic(item), 2)

    def test_light_blue_goes_to_bin_3(self):
        item = Item(4, "blue", 0.5)
        self.assertEqual(self.controller.calculate_logic(item), 3)

    def test_light_green_goes_to_bin_4(self):
        item = Item(5, "green", 0.8)
        self.assertEqual(self.controller.calculate_logic(item), 4)

    def test_unknown_color_goes_to_bin_5(self):
        item = Item(6, "yellow", 1.2)
        self.assertEqual(self.controller.calculate_logic(item), 5)

    def test_color_matching_is_case_insensitive(self):
        item = Item(7, "RED", 1.0)
        self.assertEqual(self.controller.calculate_logic(item), 2)

    # ── process_cycle ──────────────────────────────────────────────────────

    @patch("time.sleep")
    def test_process_cycle_logs_entry(self, _mock_sleep):
        item = Item(101, "Red", 2.5)
        self.controller.process_cycle(item)
        self.assertEqual(len(self.controller.operation_log), 1)
        self.assertIn("101", self.controller.operation_log[0])
        self.assertIn("1", self.controller.operation_log[0])   # Bin 1

    @patch("time.sleep")
    def test_process_cycle_invalid_item_not_logged(self, _mock_sleep):
        item = Item(999, "red", -5.0)          # invalid → sensor returns None
        self.controller.process_cycle(item)
        self.assertEqual(len(self.controller.operation_log), 0)

    @patch("time.sleep")
    def test_multiple_cycles_build_log(self, _mock_sleep):
        batch = [
            Item(101, "Red", 2.5),
            Item(102, "Blue", 0.5),
            Item(103, "Yellow", 1.2),
        ]
        for obj in batch:
            self.controller.process_cycle(obj)
        self.assertEqual(len(self.controller.operation_log), 3)


if __name__ == "__main__":
    unittest.result.TestResult.failfast = False
    unittest.main(verbosity=2)