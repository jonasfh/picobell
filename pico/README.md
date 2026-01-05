# Picobell - Pico Firmware

Firmware for the Raspberry Pi Pico W controlling the doorbell interface.

## 🚀 Quick Start

```bash
# 1. Setup Env
cd pico
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Deploy
mpremote cp -r src/* :

# 3. Monitor
mpremote repl
```

## 📚 Documentation
* **[Development & Testing](docs/DEVELOPMENT.md)**: Setup, mpremote usage, running tests.
* **[Architecture](docs/ARCHITECTURE.md)**: Pinout, modules, HAL, OTA.
* **[BLE Provisioning](docs/BLE.md)**: How to set up Wi-Fi.
* **[OTA Walkthrough](docs/OTA_WALKTHROUGH.md)**: Guide for testing firmware upgrades.

## 📂 Source Structure
* `src/`: Source code (`main.py`, `hal.py`, etc).
* `tests/`: Verification scripts (`test_main.py` for host, `test_hw.py` for device).
* `tools/`: Helper scripts.
