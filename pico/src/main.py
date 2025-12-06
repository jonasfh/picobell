# main.py
# Boot logic + button-detection + BLE provisioning
import machine
import time
import ujson
import network
from ble_provision import BLEProvision

BTN_PIN = 15
WIFI_FILE = "/flash/wifi.json"

btn = machine.Pin(BTN_PIN, machine.Pin.IN, machine.Pin.PULL_UP)


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


def save_wifi(ssid, pwd):
    with open(WIFI_FILE, "w") as f:
        ujson.dump({"ssid": ssid, "pwd": pwd}, f)


def button_held():
    if btn.value() == 0:
        t0 = time.ticks_ms()
        while btn.value() == 0:
            if time.ticks_diff(time.ticks_ms(), t0) > 4000:
                return True
            time.sleep(0.05)
    return False


# ------------------------
# Boot logic
# ------------------------
if button_held() or not has_wifi():
    print("Starting BLE provisioning...")
    prov = BLEProvision()
    prov.start()

    # provisioning loop
    while True:
        time.sleep(0.2)

else:
    print("Normal Wi-Fi startup")
    cred = load_wifi()

    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(cred["ssid"], cred["pwd"])

    for _ in range(30):
        if wifi.isconnected():
            print("Connected:", wifi.ifconfig())
            break
        time.sleep(0.3)
