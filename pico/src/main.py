# main.py - Boot + Wi-Fi + BLE + long-press reboot + ring detection
import time
import machine
import network
import ujson
import urequests
from ble_provision import BLEProvision
from version import FW_VERSION

print("Firmware version:", FW_VERSION)

BTN_PIN = 15          # long-press → reboot
RING_PIN = 10         # short press → "ring" event
WIFI_FILE = "/flash/wifi.json"

btn = machine.Pin(BTN_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
ring = machine.Pin(RING_PIN, machine.Pin.IN, machine.Pin.PULL_UP)


# ------------------------
# Utility functions
# ------------------------
def has_wifi():
    try:
        with open(WIFI_FILE) as f:
            data = ujson.load(f)
            return ("ssid" in data) and ("pwd" in data)
    except:
        return False


def load_wifi():
    with open(WIFI_FILE) as f:
        return ujson.load(f)


def connect_wifi(ssid, pwd, timeout=20):
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(ssid, pwd)
    print("Connecting:", ssid)

    t0 = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t0) < timeout * 1000:
        if wifi.isconnected():
            print("Wi-Fi OK:", wifi.ifconfig())
            return True
        time.sleep(0.3)

    print("Wi-Fi failed.")
    return False


def long_press(pin, hold_ms=10000):
    if pin.value() == 0:
        print("Button press start")
        t0 = time.ticks_ms()
        while pin.value() == 0:
            dt = time.ticks_diff(time.ticks_ms(), t0)
            if dt > hold_ms:
                return True
            time.sleep(0.1)
    return False


def short_press(pin, max_ms=300):
    # LOW = pressed; detect short momentary press
    if pin.value() == 0:
        print("Detecting short press...")
        t0 = time.ticks_ms()
        while pin.value() == 0:
            # debounce hold
            time.sleep(0.01)
        dt = time.ticks_diff(time.ticks_ms(), t0)
        return dt < max_ms
    return False


def start_ble(max_time=300):
    print("BLE start")
    prov = BLEProvision()
    prov.start()

    t0 = time.ticks_ms()
    while True:
        if prov.is_provisioned:
            print("Provision OK → reboot")
            time.sleep(0.5)
            machine.reset()

        if time.ticks_diff(time.ticks_ms(), t0) > max_time * 1000:
            print("BLE timeout")
            break

        time.sleep(0.5)


def send_ring_event(api_key):
    url = "https://picobell.no/doorbell/ring"

    headers = {
        "Authorization": "Apartment " + api_key,
        "Content-Type": "application/json",
        "X-FW-Version": FW_VERSION,
    }

    payload = {}

    try:
        print("POST:", url)
        r = urequests.post(url, headers=headers, json=payload)
        print("POST status:", r.status_code)
        r.close()
    except Exception as e:
        print("POST failed:", e)

def get_device_api_key():
    # Attempt load from wifi.json (add later in provisioning)
    try:
        with open(WIFI_FILE) as f:
            data = ujson.load(f)
            if "device_api_key" in data:
                return data["device_api_key"]
    except:
        pass

    # fallback using MAC
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    mac = wlan.config("mac")
    return mac.hex()

def check_open_status(api_key):
    url = "https://picobell.no/doorbell/status"

    headers = {
        "Authorization": "Apartment " + api_key,
        "Content-Type": "application/json",
        "X-FW-Version": FW_VERSION,
    }

    try:
        r = urequests.post(url, headers=headers, json={})
        if r.status_code == 200:
            data = r.json()
            return data.get("open", False)

        r.close()
    except Exception as e:
        print("Status check failed:", e)

    return False


def pulse_door(pin, duration=0.3):
    pin.init(machine.Pin.OUT)
    pin.value(0)
    time.sleep(duration)
    pin.init(machine.Pin.IN, machine.Pin.PULL_UP)


# ------------------------
# Boot logic
# ------------------------
print("Booting...")

device_api_key = get_device_api_key()

if not has_wifi():
    print("wifi.json missing → BLE")
    start_ble()
else:
    cred = load_wifi()
    ok = connect_wifi(cred["ssid"], cred["pwd"], 20)
    if not ok:
        print("Wi-Fi fail → BLE")
        start_ble()


# ------------------------
# Main run-loop
# ------------------------
print("Run loop...")

ring_ts = 0
status_counter = 0

while True:
    # Long press = reboot
    if long_press(btn, 10000):
        print("Long-press → reboot")
        time.sleep(0.5)
        machine.reset()

    # Short press = doorbell "ring"
    if short_press(ring, 5000):
        print("RING detected!")
        send_ring_event(device_api_key)
        ring_ts = time.time()
        status_counter = 0
        time.sleep(10)  # dont send multiple rings in a row

    # Check open-status for 5 minutes after ring
    if ring_ts and time.time() - ring_ts < 300:
        status_counter += 1

        if status_counter >= 60:
            status_counter = 0
            print("Checking open status...")
            if check_open_status(device_api_key):
                print("Åpner døren")
                pulse_door(ring)
                ring_ts = 0  # stop further checks

    time.sleep(0.05)
