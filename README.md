# Automated Item Sorting System

A Python simulation of an automated conveyor-belt sorting system. The project models the full lifecycle of sorting physical items — scanning them with sensors, deciding which bin they belong in, and moving them there with an actuator arm.

---

## What the Project Does

The system is built around four classes that work together:

- **`Item`** — Represents a physical object on the conveyor belt, described by an ID, color, and weight.
- **`SensorArray`** — Simulates an input scanner that reads an item's properties and validates them before processing.
- **`ActuatorSystem`** — Simulates the robotic arm that physically moves items into the correct bin.
- **`SortingController`** — The central brain that coordinates the full cycle: scan → decide → actuate → log.

### Sorting Logic

The controller uses a two-level decision matrix:

| Condition | Destination |
|---|---|
| Weight ≥ threshold (2.0 kg) | Bin 1 — Heavy Items |
| Light + Red | Bin 2 |
| Light + Blue | Bin 3 |
| Light + Green | Bin 4 |
| Light + Any other color | Bin 5 — Other |

Every successfully sorted item is recorded in an operation log.

---

## How to Run

```bash
python Assignment.py
```

---

## Tests

The test suite is written using Python's built-in `unittest` framework and lives in `test.py`.

### Running the Tests

```bash
python -m unittest test.py -v
```

### What the Tests Cover

**`TestItem`** — 2 tests
- Checks that an item is created with the correct `id`, `color`, and `weight`
- Verifies that `getProperties()` returns the expected dictionary

**`TestSensorArray`** — 5 tests
- Confirms a valid item is returned after a successful scan
- Confirms items with negative or zero weight are rejected and return `None`
- Directly tests `validateReadings()` for both valid and invalid input

**`TestActuatorSystem`** — 3 tests
- Checks the actuator starts with `bin_id = 0` and `is_operational = True`
- Verifies `move_to_bin()` correctly updates the current bin ID
- Verifies `resetPosition()` returns the bin ID back to 0

**`TestSortingController`** — 11 tests
- Tests every bin routing path: heavy, red, blue, green, and unknown color
- Confirms items at exactly the weight threshold go to Bin 1
- Checks that color matching is case-insensitive (e.g. `"RED"` == `"red"`)
- Verifies a completed cycle adds an entry to the operation log
- Verifies an invalid item (bad sensor reading) does not get logged
- Tests that processing multiple items builds the log correctly

### Test Results

```
Ran 21 tests in 0.007s
OK
```

All 21 tests pass. `time.sleep()` is mocked out in actuator tests so the suite runs in milliseconds.
