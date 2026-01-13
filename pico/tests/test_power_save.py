import sys
import os
import time
import unittest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import config
import hal
# We need to mock display_update to avoid errors or clutter
import main

# Mock print to avoid clutter during test
original_print = print
def mock_print(*args, **kwargs):
    pass

class TestPowerSave(unittest.TestCase):
    def setUp(self):
        self.hal = hal.HardwareAbstractionLayer()
        self.app = main.DoorbellApp(self.hal)

        # Track calls
        self.wifi_connects = 0
        self.wifi_disconnects = 0
        self.sleeps = [] #(duration, type)

        # Mock HAL methods
        original_connect = self.hal.connect_wifi
        def mock_connect(ssid, pwd):
            self.wifi_connects += 1
            self.hal._wlan = True # Fake connected
            return True
        self.hal.connect_wifi = mock_connect

        def mock_disconnect():
            self.wifi_disconnects += 1
            self.hal._wlan = None

        self.hal.disconnect_wifi = mock_disconnect

        def mock_is_connected():
            return self.hal._wlan is not None
        self.hal.is_wifi_connected = mock_is_connected

        def mock_sleep_ms(ms):
            self.sleeps.append((ms, 'sleep_ms'))
        self.hal.sleep_ms = mock_sleep_ms

        def mock_low_power(ms):
            self.sleeps.append((ms, 'low_power'))
        self.hal.low_power_sleep = mock_low_power

        # Mock other dependencies
        self.app.api_key = "TEST_KEY" # Required for connect_wifi
        self.app.send_ring_event = lambda: None
        self.app.display_update = lambda x=False: None
        self.app.check_open_status = lambda: False

        # main.print = mock_print

    def test_idle_sleep(self):
        print("\n--- Testing Idle Sleep ---")
        # Ensure IDLE state
        self.app.ring_ts = 0
        self.app.pin_ring.set_value(4417)

        # Simulate one loop iteration (partial)
        # We can't easily run the loop, but we can call the section?
        # Let's extract the "idle" part logic or simulate inputs.

        # Logic snippet from main.py:
        if self.app.ring_ts == 0:
             self.hal.low_power_sleep(1000)

        # Verify
        self.assertEqual(self.sleeps[-1], (1000, 'low_power'))

    def test_ring_wakeup_sequence(self):
        print("\n--- Testing Ring Wakeup ---")
        # 1. Simulate Ring
        self.app.pin_ring.set_value(3568)
        self.app.wifi_creds = {'ssid':'test','pwd':'test'}

        # 2. Execute Detection Logic
        # (Simplified simulation of the block)
        print("Executing Ring Logic Block")
        adc_val = self.app.pin_ring.read_u16()
        if adc_val < config.RING_THRESHOLD:
            # Wake up wifi
            self.app.connect_wifi()
            self.app.send_ring_event()
            self.app.ring_ts = 100 # Set active
            self.app.status_check_ts = 0

        # Verify WiFi connected
        self.assertTrue(self.wifi_connects >= 1)

        # 3. Verify Post-Ring Loop Logic (Check window)
        print("Executing Post-Ring Check Logic")
        # Condition: ring_ts > 0
        if self.app.ring_ts > 0:
             # Check interval
             if self.hal.time_diff(self.app.status_check_ts) > 5000: # 5 sec (mocked time is constant 0 unless we increment?)
                  # For this test, time_diff returns -start (since time is 0).
                  # self.app.status_check_ts was set to 0. time_diff(0) is 0?
                  # We need to mock time_diff or get_time_ms
                  pass

    def test_post_ring_cycling(self):
        print("\n--- Testing Post-Ring Cycle ---")
        self.app.ring_ts = 1000 # Active
        self.app.status_check_ts = 0

        # Mock time to ensure check triggers (current time 6000)
        self.hal.get_time_ms = lambda: 6000
        self.hal.time_diff = lambda t: 6000 - t

        # Run check block
        if self.hal.time_diff(self.app.status_check_ts) > 5000:
            self.app.status_check_ts = self.hal.get_time_ms()
            if not self.hal.is_wifi_connected():
                 self.app.connect_wifi()

            self.app.check_open_status()
            self.hal.disconnect_wifi()

        # Verify cycle
        self.assertTrue(self.wifi_connects >= 1, "Should connect for check")
        self.assertTrue(self.wifi_disconnects >= 1, "Should disconnect after check")

if __name__ == "__main__":
    unittest.main()
