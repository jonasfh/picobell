import framebuf
import time
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

        self.api_key = config.API_KEY
        self.wifi_creds = {
            "ssid": config.WIFI_SSID,
            "pwd": config.WIFI_PASSWORD,
        }

        # Display State
        self.app_mode = "START"
        self.last_call_str = "_________"
        self.rotation = 180 # Matches user's mounting
        self._display_last_update = self.hal.get_time_ms()

    def draw_scaled_text(self, fb, text, x, y, scale=2):
        """Draws larger text by scaling up the 8x8 font."""
        char_buf = bytearray(8)
        char_fb = framebuf.FrameBuffer(char_buf, 8, 8, framebuf.MONO_HLSB)
        for i, char in enumerate(text):
            char_fb.fill(1)
            char_fb.text(char, 0, 0, 0)
            for cy in range(8):
                for cx in range(8):
                    if char_fb.pixel(cx, cy) == 0:
                        fb.fill_rect(x + i*8*scale + cx*scale, y + cy*scale, scale, scale, 0)

    def display_update(self, partial=False):
        """Redraws the status screen and sleeps the display to save battery."""
        # Force partial=False per user request for full screen refreshes
        partial = False

        epd = self.hal.get_epd()
        epd.init() # Wake up / Reset chip

        # 1. Create a "Virtual" buffer to draw on
        width, height = 200, 200
        buf = bytearray(width * height // 8)
        fb = framebuf.FrameBuffer(buf, width, height, framebuf.MONO_HLSB)
        fb.fill(1) # White

        # Draw Content
        self.draw_scaled_text(fb, "PICOBELL", 10, 15, scale=3)

        ssid = self.wifi_creds.get("ssid", "NONE")
        if not self.hal.is_wifi_connected():
            wifi_str = "OFF"
        else:
            wifi_str = ssid[:6] # Keep it centered/concise

        self.draw_scaled_text(fb, f"WIFI {wifi_str}", 10, 60, scale=2)
        self.draw_scaled_text(fb, f"MODE {self.app_mode}", 10, 85, scale=2)
        self.draw_scaled_text(fb, f"LAST CALL", 10, 110, scale=2)
        self.draw_scaled_text(fb, f"{self.last_call_str}", 10, 135, scale=2)
        self.draw_scaled_text(fb, f"SOFTWARE VERSION {FW_VERSION}", 10, 180, scale=1)

        # Border
        fb.rect(2, 2, 196, 196, 0)

        # 2. Software Rotation
        ready_buf = buf
        if self.rotation == 180:
            ready_buf = bytearray(len(buf))
            dst_fb = framebuf.FrameBuffer(ready_buf, width, height, framebuf.MONO_HLSB)
            dst_fb.fill(1)
            for y in range(height):
                for x in range(width):
                    pixel = fb.pixel(x, y)
                    dst_fb.pixel(width - 1 - x, height - 1 - y, pixel)

        # 3. Push to display
        if partial:
            epd.display_partial(ready_buf)
        else:
            epd.clear(fast=False)
            epd.display(ready_buf)

        epd.sleep() # Deep sleep saves significant power
        self._display_last_update = self.hal.get_time_ms()

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

    def get_api_key(self):
        if self.api_key:
            return self.api_key
        # Fallback to MAC
        return self.hal.get_mac_address()

    def connect_wifi(self):
        if not self.api_key:
            return False

        print("Connecting to Wi-Fi...")
        if self.hal.connect_wifi(self.wifi_creds["ssid"], self.wifi_creds["pwd"]):
            print("Wi-Fi Connected")
            return True
        print("Wi-Fi Connection Failed")
        return False

    def start_ble_provisioning(self, timeout_ms=600000):
        """
        Starts BLE provisioning mode.
        Default timeout is 10 minutes (600000 ms).
        """
        print(f"Starting BLE Provisioning (Timeout: {timeout_ms/600000} mins)...")
        if not BLEProvision:
            print("BLE module not available")
            return

        self.app_mode = "SETUP"
        self.display_update()

        self.led_mode = 2
        # Initialize BLEProvision with self.hal
        prov = BLEProvision(self.hal)
        prov.start()

        t0 = self.hal.get_time_ms()
        while True:
            if prov.is_provisioned:
                print("Provisioned! Rebooting...")
                self.hal.sleep(1.0) # Give time for BLE to finish notification
                self.hal.reset_device()

            # Check timeout
            if self.hal.time_diff(t0) > timeout_ms:
                print("BLE Provisioning Timeout. Returning to normal operation.")
                self.led_mode = 0 # Turn off LED animation
                self.pin_led.off()
                self.display_update()
                break

            self.led_update()
            self.hal.sleep_ms(100)

    def send_ring_event(self):
        url = config.URL_RING

        print("Sending RING event...")
        r = self.hal.http_post(url, {}, {})
        if r:
            try:
                data = r.json()
                ts = data.get("unix_timestamp")
                if ts:
                    self.hal.set_time(ts)
                    # Format: WED 22:35 (6+ chars, but we keep it concise)
                    days = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
                    tm = time.localtime(ts)
                    self.last_call_str = f"{days[tm[6]]} {tm[3]:02d}:{tm[4]:02d}"
                    print(f"Server time sync: {self.last_call_str}")
                r.close()
            except Exception as e:
                print(f"Error parsing ring response: {e}")

        self.display_update(partial=True)

    def check_open_status(self):
        url = config.URL_STATUS
        r = self.hal.http_post(url, {}, {})
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
        self.app_mode = "OPEN"
        self.display_update()

        self.pin_door.on()
        self.hal.sleep(config.DOOR_PULSE_S)
        self.pin_door.off()

        self.app_mode = "LISTEN"
        self.display_update()

    def run(self):
        print(f"Booting Firmware {FW_VERSION}")
        # Note: We wait to display until WiFi or BLE mode is ready
        if not self.wifi_creds or not self.wifi_creds.get("ssid"):
            print("No Wi-Fi credentials found.")
            self.start_ble_provisioning()
        else:
            if self.connect_wifi():
                self.led_mode = 1
                self.app_mode = "LISTEN"
                self.display_update()
                # Check OTA
                if self.ota.check_for_updates():
                    self.ota.update_firmware()
            else:
                print("Could not connect to Wi-Fi. Returning to Setup.")
                self.app_mode = "SETUP"
                self.display_update()
                self.start_ble_provisioning()

        # 2. Main Loop
        print("Entering Main Loop")
        while True:
            # LED Animation
            self.led_update()

            # Button handling (Manual Door Open vs BLE Setup)
            if self.pin_btn.value() == 0:
                # Button pressed
                t_press = self.hal.get_time_ms()
                is_long_press = False

                # Check for hold
                while self.pin_btn.value() == 0:
                    self.hal.sleep_ms(100)
                    if self.hal.time_diff(t_press) > 10000: # 10 sec hold
                         is_long_press = True
                         print("Button Hold (10s) -> BLE Provisioning")
                         self.start_ble_provisioning()
                         break

                if not is_long_press:
                    # Short press (<10s) -> Open Door
                    # Debounce check
                    if self.hal.time_diff(t_press) > 50:
                        self.pulse_door()

                # Wait for release to avoid re-triggering
                while self.pin_btn.value() == 0:
                    self.hal.sleep_ms(100)

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
