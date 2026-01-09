# config.py
# Configuration constants

try:
    import ujson as json
except ImportError:
    import json

# Hardware Pins
PIN_BTN_BOOT = 15      # Long-press to reboot/enter provisioning
# change pin for ring input so it dont use the same pin as the busy signal
PIN_RING_IN = 12       # Input from Optocoupler (Doorbell Ring)
PIN_DOOR_OUT = 11      # Output to Optocoupler (Door Opener)
PIN_LED = "LED"        # Onboard LED

# E-Ink Display Pins (Waveshare 1.54" V2)
PIN_EPD_DIN = 7        # MOSI (GP7)
PIN_EPD_CLK = 6        # SCLK (GP6)
PIN_EPD_CS = 5         # SPI CS (GP5)
PIN_EPD_DC = 8         # Data/Command (GP8)
PIN_EPD_RST = 9        # Reset (GP9)
PIN_EPD_BUSY = 10      # Busy Signal (GP10)

# Filesystem
FILE_WIFI = "/flash/wifi.json"

# Timing
RING_DEBOUNCE_MS = 300
DOOR_PULSE_S = 0.3
STATUS_CHECK_INTERVAL_S = 10  # Check for open status every 10s after ring
STATUS_CHECK_DURATION_S = 300 # Keep checking for 5 minutes

# --- Load Configuration ---

def load_config(file_wifi):
    data = {}
    try:
        with open(file_wifi, 'r') as f:
            data = json.load(f)
    except Exception:
        # Fallback for testing on host
        try:
             with open("wifi.json", 'r') as f:
                data = json.load(f)
        except:
            pass
    return data

_config_data = load_config(FILE_WIFI)

# Exposed Variables
WIFI_SSID = _config_data.get("ssid")
WIFI_PASSWORD = _config_data.get("pwd")
API_KEY = _config_data.get("device_api_key")

# Allow overriding BASE_URL from wifi.json for testing
BASE_URL = _config_data.get("base_url", "https://picobell.no")

# API Endpoints (Computed after BASE_URL is resolved)
URL_RING = BASE_URL + "/doorbell/ring"
URL_STATUS = BASE_URL + "/doorbell/status"
URL_OTA_VERSION = BASE_URL + "/pico/fw_version"
URL_OTA_FILES = BASE_URL + "/pico/list_py_files"
