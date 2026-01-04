# Development & Testing

## TL;DR
1. **Connect** Pico via USB.
2. **Setup**: `cd pico && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
3. **Deploy**: `mpremote cp -r src/* :`
4. **Test (Logic)**: `python3 -m unittest discover tests`
5. **Test (HW)**: `mpremote run tests/test_hw.py`

---

## 1. Environment Setup
We use `mpremote` (MicroPython Remote Control) instead of Thonny for a cleaner, CLI-based workflow.

### Initial Setup
```bash
cd pico
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Common Commands
All paths on the Pico are prefixed with `:`.
* `.` = local current directory
* `:` = root of the Pico filesystem

| Action | Command | Note |
| :--- | :--- | :--- |
| **List files** | `mpremote ls` | |
| **Upload file** | `mpremote cp local_file.py :` | Copies to root |
| **Upload folder** | `mpremote cp -r src/ :` | Wraps contents in folder? No, creates `src` on device. |
| **Upload content** | `mpremote cp -r src/* :` | Copies *contents* of src to root |
| **Download** | `mpremote cp :wifi.json .` | Copy from device to local |
| **Remove file** | `mpremote rm :old_file.py` | |
| **Remove dir** | `mpremote rmdir :folder` | Directory must be empty! |
| **Remove recursive** | `mpremote run tools/cleanup.py` | (Custom script often needed for `rm -rf`) |
| **Read file** | `mpremote cat :boot.py` | Print content to terminal |
| **Soft Reset** | `mpremote soft-reset` | Restarts the app |
| **REPL** | `mpremote repl` | Ctrl+] to exit |

> **Tip:** `mpremote` does not have a native `rm -r` (recursive delete). If you need to wipe a directory like `__pycache__` on the device, you often have to use `rm` on each file or use Python in the REPL:
> `mpremote exec "import shutil; shutil.rmtree('/__pycache__')"` (if shutil is available, or use `os.remove`).


---

## 2. Testing

### Host-based Logic Tests
These tests run on your computer and verify the application logic using **Mocks**. No Pico required.
```bash
python3 -m unittest discover tests
```

### On-Device Hardware Tests
These scripts run on the Pico itself to verify wiring (LEDs, Optocouplers).
```bash
# Ensure test file is up to date (or run directly)
mpremote run tests/test_hw.py
```

### Manual Testing with REPL
You can interact with the hardware interactively:
```bash
mpremote repl
>>> import machine
>>> p10 = machine.Pin(10, machine.Pin.IN, machine.Pin.PULL_UP)
>>> p10.value() # Check if ring is pressed (0) or released (1)
```

## 3. Firmware Flashing
If you need to reinstall MicroPython:
1. Download newest UF2 from [micropython.org](https://micropython.org/download/rp2-picow/).
2. Hold **BOOTSEL** button while plugging in USB.
3. Copy `.uf2` file to the `RPI-RP2` drive.
