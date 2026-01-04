# config.py
# Configuration constants

# Hardware Pins
PIN_BTN_BOOT = 15      # Long-press to reboot/enter provisioning
PIN_RING_IN = 10       # Input from Optocoupler (Doorbell Ring)
PIN_DOOR_OUT = 11      # Output to Optocoupler (Door Opener)
PIN_LED = "LED"        # Onboard LED

# Filesystem
FILE_WIFI = "/flash/wifi.json"

# API Endpoints
BASE_URL = "https://picobell.no"
URL_RING = BASE_URL + "/doorbell/ring"
URL_STATUS = BASE_URL + "/doorbell/status"
URL_OTA_VERSION = BASE_URL + "/pico/fw_version"
URL_OTA_FILES = BASE_URL + "/pico/list_py_files"

# Timing
RING_DEBOUNCE_MS = 300
DOOR_PULSE_S = 0.3
STATUS_CHECK_INTERVAL_S = 10  # Check for open status every 10s after ring
STATUS_CHECK_DURATION_S = 300 # Keep checking for 5 minutes

try:
    import ujson as json
except ImportError:
    import json

# Load config from flash/wifi.json
def load_wifi_creds(file_wifi):
    data = None
    with open(file_wifi, 'r') as f:
        data = json.load(f)

    if data and "ssid" in data and "pwd" in data and "device_api_key" in data:
        return (data["pwd"], data["device_api_key"], data["ssid"])
    return (None, None, None)

(WIFI_PASSWORD, API_KEY, WIFI_SSID) = load_wifi_creds(FILE_WIFI)
