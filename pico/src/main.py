# main.py
# Boot logic with automatic BLE provisioning fallback
import time
import machine
import network
import ujson
from ble_provision import BLEProvision

WIFI_FILE = "/flash/wifi.json"


def has_wifi():
    try:
        with open(WIFI_FILE) as f:
            data = ujson.load(f)
            return "ssid" in data and "pwd" in data
    except:
        return False


def load_wifi():
    with open(WIFI_FILE) as f:
        return ujson.load(f)


def connect_wifi(ssid, pwd, timeout=20):
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(ssid, pwd)
    print("Connecting to Wi-Fi:", ssid)

    t0 = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), t0) < timeout * 1000:
        if wifi.isconnected():
            print("Wi-Fi OK:", wifi.ifconfig())
            return True
        time.sleep(0.3)

    print("Wi-Fi connect failed.")
    return False


def start_ble_provision(max_time=300):
    print("Starting BLE provisioning...")
    prov = BLEProvision()
    prov.start()

    t0 = time.ticks_ms()
    while True:
        if prov.is_provisioned:
            print("Provisioned. Rebooting...")
            time.sleep(0.5)
            machine.reset()
        if time.ticks_diff(time.ticks_ms(), t0) > max_time * 1000:
            print("BLE timeout. Exiting provisioning.")
            break
        time.sleep(0.5)


# ------------------------
# Boot logic
# ------------------------
print("Booting Pico...")

if not has_wifi():
    print("No wifi.json → BLE provisioning.")
    start_ble_provision()
else:
    cred = load_wifi()
    ok = connect_wifi(cred["ssid"], cred["pwd"], timeout=20)
    if not ok:
        print("Wi-Fi failed → BLE provisioning.")
        start_ble_provision()
