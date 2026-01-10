# hal.py
import sys
import time
import config
from version import FW_VERSION


# Try importing MicroPython modules, otherwise use mocks for testing on host
IS_MICROPYTHON = False
try:
    import machine
    import network
    import urequests
    import ujson
    import utime
    IS_MICROPYTHON = True
except ImportError:
    # Minimal mocks for host testing context
    machine = None
    network = None
    urequests = None
    ujson = None

class HardwareAbstractionLayer:
    def __init__(self):
        self._wlan = None

    def get_time_ms(self):
        """Returns current time in milliseconds."""
        if IS_MICROPYTHON:
            return time.ticks_ms()
        return int(time.time() * 1000)

    def time_diff(self, t_start):
        """Returns difference in milliseconds."""
        if IS_MICROPYTHON:
            return time.ticks_diff(time.ticks_ms(), t_start)
        return int(time.time() * 1000) - t_start

    def sleep_ms(self, duration_ms):
        time.sleep(duration_ms / 1000.0)

    def sleep(self, duration_s):
        time.sleep(duration_s)

    def file_exists(self, filepath):
        try:
            with open(filepath, 'r'):
                return True
        except:
            return False

    def load_json(self, filepath):
        if not self.file_exists(filepath):
            return None
        with open(filepath, 'r') as f:
            if IS_MICROPYTHON:
                return ujson.load(f)
            import json
            return json.load(f)

    def save_json(self, filepath, data):
        with open(filepath, 'w') as f:
            if IS_MICROPYTHON:
                ujson.dump(data, f)
            else:
                import json
                json.dump(data, f)

    def reset_device(self):
        if IS_MICROPYTHON:
            machine.reset()
        else:
            print("[HAL] Reset device triggered")

    # --- Pin Management ---
    def create_pin_in(self, pin_id, pull_up=True):
        if IS_MICROPYTHON:
            pull = machine.Pin.PULL_UP if pull_up else None
            return machine.Pin(pin_id, machine.Pin.IN, pull)
        else:
            return MockPin(pin_id, 0 if pull_up else 1)

    def create_pin_out(self, pin_id):
        if IS_MICROPYTHON:
            return machine.Pin(pin_id, machine.Pin.OUT)
        else:
            return MockPin(pin_id, 0)

    # --- SPI Management ---
    def create_spi(self, spi_id, baudrate, sck_pin, mosi_pin, miso_pin=None):
        if IS_MICROPYTHON:
            import machine
            miso = machine.Pin(miso_pin) if miso_pin is not None else None
            return machine.SPI(spi_id, baudrate=baudrate, sck=machine.Pin(sck_pin), mosi=machine.Pin(mosi_pin), miso=miso)
        else:
            return MockSPI()

    def get_epd(self):
        """Returns initialized E-Ink display object."""
        if not hasattr(self, '_epd'):
            if IS_MICROPYTHON:
                from epaper1in54 import EPD
                # Standard Waveshare SPI config
                spi = self.create_spi(0, baudrate=4000000,
                                     sck_pin=config.PIN_EPD_CLK,
                                     mosi_pin=config.PIN_EPD_DIN)
                cs = self.create_pin_out(config.PIN_EPD_CS)
                dc = self.create_pin_out(config.PIN_EPD_DC)
                rst = self.create_pin_out(config.PIN_EPD_RST)
                busy = self.create_pin_in(config.PIN_EPD_BUSY, pull_up=False)

                self._epd = EPD(spi, cs, dc, rst, busy)
                self._epd.init()
            else:
                self._epd = MockEPD()
        return self._epd

    # --- Time Management ---
    def set_time(self, unix_timestamp):
        """Sets the system RTC from a unix timestamp."""
        if IS_MICROPYTHON:
            # RTC tuple: (year, month, day, weekday, hours, minutes, seconds, subseconds)
            tm = time.localtime(unix_timestamp)
            rtc = machine.RTC()
            rtc.datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))
            print(f"[HAL] Time synced: {tm}")
        else:
            print(f"[HAL] Mock time set to {unix_timestamp}")

    def get_uptime_str(self):
        """Returns uptime as 'Xd Yh Zm'."""
        ms = self.get_time_ms()
        seconds = ms // 1000
        minutes = seconds // 60
        hours = minutes // 60
        days = hours // 24

        return f"{days}d {hours % 24}h {minutes % 60}m"

    # --- Network ---
    def connect_wifi(self, ssid, password, timeout_s=20):
        if not IS_MICROPYTHON:
            print(f"[HAL] Mock connecting to WiFi: {ssid}")
            return True

        self._wlan = network.WLAN(network.STA_IF)
        self._wlan.active(True)
        self._wlan.connect(ssid, password)

        t0 = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), t0) < timeout_s * 1000:
            if self._wlan.isconnected():
                return True
            time.sleep(0.3)
        return False

    def is_wifi_connected(self):
        if not IS_MICROPYTHON:
            return True
        if not self._wlan:
            return False
        return self._wlan.isconnected()

    def get_mac_address(self):
        if not IS_MICROPYTHON:
            return "001122334455"

        if not self._wlan:
            self._wlan = network.WLAN(network.STA_IF)
            self._wlan.active(True)
        return self._wlan.config("mac").hex()

    # --- HTTP ---
    def http_post(self, url, headers, json_data):

        all_headers = {
            "Authorization": "Apartment " + config.API_KEY,
            "Content-Type": "application/json",
            "X-FW-Version": FW_VERSION,
        }
        all_headers.update(headers)

        if not IS_MICROPYTHON:
            print(f"[HAL] Mock POST to {url} with {json_data}")
            return MockResponse(200, {})

        try:
            r = urequests.post(url, headers=all_headers, json=json_data)
            return r
        except Exception as e:
            print(f"HTTP Error: {e}")
            return None

    def http_get(self, url, headers={}):
        all_headers = {
            "Authorization": "Apartment " + config.API_KEY,
            "Content-Type": "application/json",
            "X-FW-Version": FW_VERSION,
        }
        all_headers.update(headers)
        if not IS_MICROPYTHON:
            print(f"[HAL] Mock GET from {url}")
            return MockResponse(200, {})

        try:
            r = urequests.get(url, headers=all_headers)
            return r
        except Exception as e:
            print(f"HTTP Error: {e}")
            return None


# --- Mocks for Host Testing ---
class MockPin:
    def __init__(self, pin_id, initial_value):
        self.pin_id = pin_id
        self._value = initial_value

    def value(self, val=None):
        if val is not None:
            self._value = val
        return self._value

    def on(self):
        self._value = 1

    def off(self):
        self._value = 0

class MockResponse:
    def __init__(self, status_code, json_content):
        self.status_code = status_code
        self._json = json_content
        import json
        self._text = json.dumps(json_content)

    def json(self):
        return self._json

    @property
    def text(self):
        return self._text

    def close(self):
        pass


class MockSPI:
    def init(self, *args, **kwargs):
        pass

    def write(self, data):
        pass


class MockEPD:
    def init(self):
        print("[HAL] Mock EPD initialized")

    def sleep(self):
        print("[HAL] Mock EPD sleep")

    def display(self, image):
        print("[HAL] Mock EPD display image")

    def clear(self, fast=False):
        print("[HAL] Mock EPD clear")
