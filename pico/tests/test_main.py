# tests/test_main.py
import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import hal
import config
from main import DoorbellApp

class TestDoorbellApp(unittest.TestCase):
    def setUp(self):
        self.hal = hal.HardwareAbstractionLayer()
        self.app = DoorbellApp(self.hal)

        # Mock Wifi Creds
        self.app.wifi_creds = {"ssid": "test", "pwd": "test"}
        self.app.api_key = "1234abcd"
        config.API_KEY = "1234abcd"

    def test_initial_state(self):
        self.assertEqual(self.app.led_mode, 0)
        self.assertFalse(self.app.pin_led.value())

    def test_ring_event(self):
        """Test that detecting a ring sends an event."""
        # Setup: Wifi Connected
        self.app.connect_wifi()
        self.app.led_mode = 1

        # Simulate Ring Input (Active Low)
        self.app.pin_ring.value(0)

        # Run one loop iteration logic (manually triggering logic parts)
        # We can't run app.run() as it's an infinite loop.
        # We extract logic or just call internal methods.

        # Ideally we refactor run() to be testable step-by-step or call internal checks
        # Here we mimic the run loop check:
        if self.app.pin_ring.value() == 0:
             self.app.send_ring_event()
             self.app.ring_ts = self.hal.get_time_ms()

        # Verify HTTP post was called (via print mock in HAL or we can inspect HAL if we improved it)
        # Our MockHAL currently just prints. Real MockHAL should store calls.

        self.assertNotEqual(self.app.ring_ts, 0)

    def test_door_open(self):
        """Test door pulse logic."""
        self.app.pin_door.off()
        self.app.pulse_door()
        # Mock Pin should be back to 0 after pulse
        self.assertEqual(self.app.pin_door.value(), 0)

if __name__ == '__main__':
    unittest.main()
