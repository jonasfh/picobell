# main.py
import sys
import hal
import config
from ota import OTAUpdater
from version import FW_VERSION

# Try to import BLE, but allow failure for host testing if not mocked/available
try:
    from ble_provision import BLEProvision
except ImportError:
    BLEProvision = None

class DoorbellApp:
    def __init__(self, hardware_layer):
        self.hal = hardware_layer
        self.ota = OTAUpdater(self.hal, FW_VERSION)

        # Pins
        self.pin_btn = self.hal.create_pin_in(config.PIN_BTN_BOOT, pull_up=True)
        self.pin_ring = self.hal.create_pin_in(config.PIN_RING_IN, pull_up=True) # Input from Optocoupler
        self.pin_door = self.hal.create_pin_out(config.PIN_DOOR_OUT)             # Output to Optocoupler

        # We assume LED pin is handled by HAL or machine but HAL.create_pin_out can handle "LED" string if implemented
        # Our HAL implementation: create_pin_out(pin_id)
        # config.PIN_LED is "LED"
        self.pin_led = self.hal.create_pin_out(config.PIN_LED)
        self.pin_led.off()

        # State
        self.led_state = 0
        self.led_last_toggle = 0
        self.led_mode = 0 # 0=OFF, 1=WIFI, 2=BLE

        self.ring_ts = 0
        self.status_check_ts = 0

        self.api_key = None
        self.wifi_creds = None

    def led_update(self):
        now = self.hal.get_time_ms()

        if self.led_mode == 1: # WIFI (Short blink)
            if self.hal.time_diff(self.led_last_toggle) > 2000:
                self.pin_led.on()
                self.led_state = 1
                self.led_last_toggle = now
            elif self.led_state == 1 and self.hal.time_diff(self.led_last_toggle) > 100:
                self.pin_led.off()
                self.led_state = 0

        elif self.led_mode == 2: # BLE (Fast toggle)
            if self.hal.time_diff(self.led_last_toggle) > 500:
                self.pin_led.value(not self.pin_led.value())
                self.led_last_toggle = now

    def load_wifi_creds(self):
        data = self.hal.load_json(config.FILE_WIFI)
        if data and "ssid" in data and "pwd" in data:
            self.wifi_creds = data
            if "device_api_key" in data:
                self.api_key = data["device_api_key"]
            return True
        return False

    def get_api_key(self):
        if self.api_key:
            return self.api_key
        # Fallback to MAC
        return self.hal.get_mac_address()

    def connect_wifi(self):
        if not self.wifi_creds:
            return False

        print("Connecting to Wi-Fi...")
        if self.hal.connect_wifi(self.wifi_creds["ssid"], self.wifi_creds["pwd"]):
            print("Wi-Fi Connected")
            return True
        print("Wi-Fi Connection Failed")
        return False

    def start_ble_provisioning(self):
        print("Starting BLE Provisioning...")
        if not BLEProvision:
            print("BLE module not available")
            return

        self.led_mode = 2
        prov = BLEProvision()
        prov.start()

        t0 = self.hal.get_time_ms()
        while True:
            if prov.is_provisioned:
                print("Provisioned! Rebooting...")
                self.hal.sleep(0.5)
                self.hal.reset_device()

            # Timeout 5 mins
            if self.hal.time_diff(t0) > 300000:
                print("BLE Timeout")
                break

            self.led_update()
            self.hal.sleep_ms(100)

    def send_ring_event(self):
        url = config.URL_RING
        key = self.get_api_key()
        headers = {
            "Authorization": "Apartment " + key,
            "Content-Type": "application/json",
            "X-FW-Version": FW_VERSION,
        }
        print("Sending RING event...")
        self.hal.http_post(url, headers, {})

    def check_open_status(self):
        url = config.URL_STATUS
        key = self.get_api_key()
        headers = {
            "Authorization": "Apartment " + key,
            "Content-Type": "application/json",
            "X-FW-Version": FW_VERSION,
        }

        r = self.hal.http_post(url, headers, {})
        if r:
            try:
                data = r.json()
                r.close()
                return data.get("open", False)
            except:
                pass
        return False

    def pulse_door(self):
        print("OPENING DOOR")
        # Pulse Output Pin (simulating button press on door controller via optocoupler)
        # Usually active low or high depending on wiring.
        # Assuming Optocoupler needs HIGH to activate, or LOW.
        # Let's assume Active High for now (Pin=1 -> Opto ON -> Door Input Closed).
        self.pin_door.on()
        self.hal.sleep(config.DOOR_PULSE_S)
        self.pin_door.off()

    def run(self):
        print(f"Booting Firmware {FW_VERSION}")

        # 1. Boot Checks
        if not self.load_wifi_creds():
            print("No Wi-Fi credentials found.")
            self.start_ble_provisioning()
        else:
            if self.connect_wifi():
                self.led_mode = 1
                # Check OTA
                if self.ota.check_for_updates():
                    self.ota.update_firmware()
            else:
                print("Could not connect to Wi-Fi.")
                self.start_ble_provisioning()

        # 2. Main Loop
        print("Entering Main Loop")
        while True:
            # LED Animation
            self.led_update()

            # Button: Long press for reboot/BLE
            if self.pin_btn.value() == 0:
                # Basic debounce/hold check
                t_press = self.hal.get_time_ms()
                while self.pin_btn.value() == 0:
                    self.hal.sleep_ms(100)
                    if self.hal.time_diff(t_press) > 5000: # 5 sec hold
                         print("Button Hold -> RESET")
                         self.hal.reset_device()

            # Ring Pin: Input (normally HIGH, LOW when pressed/active if pullup)
            # Optocoupler input: If opto closes to GND, then LOW.
            if self.pin_ring.value() == 0:
                # Debounce
                self.hal.sleep_ms(50)
                if self.pin_ring.value() == 0:
                    print("RING Detected")
                    if self.led_mode == 1: # Only if wifi connected
                         self.send_ring_event()
                         self.ring_ts = self.hal.get_time_ms() # Start checking window
                         self.status_check_ts = self.hal.get_time_ms()

                    # Wait for release to avoid multiple triggers
                    while self.pin_ring.value() == 0:
                        self.hal.sleep_ms(100)

            # Check for open command if within window
            if self.ring_ts > 0:
                # Window: 5 mins
                if self.hal.time_diff(self.ring_ts) > config.STATUS_CHECK_DURATION_S * 1000:
                    self.ring_ts = 0 # Window expired

                else:
                    # Check every 10s
                    if self.hal.time_diff(self.status_check_ts) > config.STATUS_CHECK_INTERVAL_S * 1000:
                        self.status_check_ts = self.hal.get_time_ms()
                        print("Checking door status...")
                        if self.check_open_status():
                            self.pulse_door()
                            self.ring_ts = 0 # Stop checking after open

            self.hal.sleep_ms(50)


if __name__ == "__main__":
    hw = hal.HardwareAbstractionLayer()
    app = DoorbellApp(hw)
    app.run()
