# main.py - Boot + Wi-Fi + BLE + long-press reboot + ring detection
import time
import machine
import network
import ujson
import urequests
from ble_provision import BLEProvision

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


def send_ring_event(device_id):
    url = "https://picobell.no/doorbell/ring"
    payload = {"pico_serial": device_id}
    try:
        print("POST:", payload)
        r = urequests.post(url, json=payload)
        print("POST status:", r.status_code)
        r.close()
    except Exception as e:
        print("POST failed:", e)


def get_device_id():
    # Attempt load from wifi.json (add later in provisioning)
    try:
        with open(WIFI_FILE) as f:
            data = ujson.load(f)
            if "device_id" in data:
                return data["device_id"]
    except:
        pass

    # fallback using MAC
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    mac = wlan.config("mac")
    return mac.hex()


# ------------------------
# Boot logic
# ------------------------
print("Booting...")

device_id = get_device_id()

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

while True:
    # Long press = reboot
    if long_press(btn, 10000):
        print("Long-press → reboot")
        time.sleep(0.5)
        machine.reset()

    # Short press = doorbell "ring"
    if short_press(ring, 500):
        print("RING detected!")
        send_ring_event(device_id)

    time.sleep(0.05)
