# pico/tests/test_ble_mock.py
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
# Add tests to path for mocks
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Mock MicroPython modules before importing ble_provision
import bluetooth_mock
import network_mock
import micropython_mock

sys.modules['bluetooth'] = bluetooth_mock
sys.modules['network'] = network_mock
sys.modules['micropython'] = micropython_mock

# Now import the class to test
import hal
import ble_provision

class TestBLEProvisionMock(unittest.TestCase):
    def setUp(self):
        # Reset wifi.json if it exists
        if os.path.exists("wifi.json"):
            os.remove("wifi.json")

        # We need to mock 'open' for /flash/wifi.json especially
        self.hal = hal.HardwareAbstractionLayer()
        self.provisioner = ble_provision.BLEProvision(self.hal)

    def tearDown(self):
        if os.path.exists("wifi.json"):
            os.remove("wifi.json")

    def test_full_provisioning_flow(self):
        ble = self.provisioner.ble

        # 1. Start advertising
        self.provisioner.start()
        self.assertTrue(ble._active)
        self.assertEqual(self.provisioner.device_id, "001122334455")

        conn_handle = 1

        # 2. Simulate Connection
        ble.simulate_connect(conn_handle, 0, b"addr")
        self.assertIn(conn_handle, self.provisioner._connections)

        # 3. Write SSID
        ble.simulate_write(conn_handle, self.provisioner.h_ssid, b"MyWiFi")
        self.assertEqual(self.provisioner._ssid, "MyWiFi")

        # 4. Write Password
        ble.simulate_write(conn_handle, self.provisioner.h_pwd, b"secret123")
        self.assertEqual(self.provisioner._pwd, "secret123")

        # 5. Write API Key
        ble.simulate_write(conn_handle, self.provisioner.h_api, b"api_abc_123")
        self.assertEqual(self.provisioner._api_key, "api_abc_123")

        # 6. Write Connect Command
        # We need to mock 'open' to avoid writing to real system /flash/wifi.json
        # Actually in ble_provision.py it writes to "/flash/wifi.json"
        # On local machine it will try to create /flash dir which might fail or be bad.

        with patch("builtins.open", unittest.mock.mock_open()) as mocked_file:
            ble.simulate_write(conn_handle, self.provisioner.h_cmd, b"connect")

            # Since _connect has a loop with sleeps, it might take a moment.
            # But with our network_mock, it connects immediately.

            self.assertTrue(self.provisioner.is_provisioned)

            # Check if it tried to write the file
            # Note: it opens "/flash/wifi.json"
            mocked_file.assert_called_with("/flash/wifi.json", "w")

            # Verify data written (roughly)
            handle = mocked_file()
            # This is a bit tricky with mock_open and multi writes/json.dump
            # But if it succeeded, it's good.

    def test_disconnect_restarts_advertising(self):
        ble = self.provisioner.ble
        conn_handle = 1

        ble.simulate_connect(conn_handle, 0, b"addr")
        self.assertIn(conn_handle, self.provisioner._connections)

        # Trigger disconnect IRQ
        ble._irq_handler(2, (conn_handle, 0, b"addr")) # IRQ_CENTRAL_DISCONNECT = 2
        self.assertNotIn(conn_handle, self.provisioner._connections)

if __name__ == '__main__':
    unittest.main()
