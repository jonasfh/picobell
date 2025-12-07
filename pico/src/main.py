# main.py - Picobell boot + BLE + Wi-Fi + long-press reboot
import time
import machine
import network
import ujson
from ble_provision import BLEProvision

BTN_PIN = 15
WIFI_FILE = "/flash/wifi.json"

btn = machine.Pin(BTN_PIN, machine.Pin.IN, machine.Pin.PULL_UP)


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


def start_ble(max_time=300):
    print("BLE provision start")
    prov = BLEProvision()
    prov.start()

    t0 = time.ticks_ms()
    while True:
        if prov.is_provisioned:
            print("Provision OK → reboot")
            time.sleep(0.5)
            machine.reset()
        if time.ticks_diff(time.ticks_ms(), t0) > max_time * 1000:
            print("BLE timeout → exit")
            break
        time.sleep(0.5)


# ------------------------
# Boot logic
# ------------------------
print("Booting...")

# 1. Wi-Fi missing → BLE
if not has_wifi():
    print("wifi.json missing → BLE")
    start_ble()

# 2. Wi-Fi present → try connect
else:
    cred = load_wifi()
    ok = connect_wifi(cred["ssid"], cred["pwd"], 20)
    if not ok:
        print("Wi-Fi fail → BLE")
        start_ble()


# ------------------------
# Main run-loop
# ------------------------
print("Run loop started.")

while True:
    # Detect long-press for reboot only
    if long_press(btn, 10000):
        print("Long-press → reboot")
        time.sleep(0.5)
        machine.reset()
        break

    # TODO: port-relay logic / heartbeat / mqtt etc.
    time.sleep(0.1)
