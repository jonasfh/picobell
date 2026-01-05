import unittest
import sys
import os
import shutil
import time
import requests

# Add src to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import config
import ota
from hal import HardwareAbstractionLayer

class RealPcHal(HardwareAbstractionLayer):
    """
    HAL implementation that uses real PC networking via requests.
    This simulates what the Pico does but using Python's request library
    to actually hit the localhost server.
    """
    def __init__(self):
        super().__init__()

    def http_get(self, url, headers={}):
        all_headers = {
            "Authorization": "Apartment " + config.API_KEY,
            "Content-Type": "application/json",
        }
        all_headers.update(headers)

        print(f"[RealPcHal] GET {url}")
        try:
            r = requests.get(url, headers=all_headers)

            # Create a mock-like object that behaves like the urequests response object
            class ResponseWrapper:
                def __init__(self, response):
                    self.r = response
                    self.status_code = response.status_code
                    self.text = response.text

                def json(self):
                    return self.r.json()

                def close(self):
                    pass

            return ResponseWrapper(r)
        except Exception as e:
            print(f"[RealPcHal] Request failed: {e}")
            return None

class TestOtaIntegration(unittest.TestCase):
    def setUp(self):
        # Override config to point to local server
        self.original_url_version = config.URL_OTA_VERSION
        self.original_url_files = config.URL_OTA_FILES
        self.original_base_url = config.BASE_URL

        # Point to the local PHP server
        # Assuming php -S 0.0.0.0:8080 -t public
        LOCAL_BASE = "http://localhost:8080"

        config.BASE_URL = LOCAL_BASE
        config.URL_OTA_VERSION = LOCAL_BASE + "/pico/fw_version"
        config.URL_OTA_FILES = LOCAL_BASE + "/pico/list_py_files"

        # Use the test API key (ensure 'TestApiKeySeeder' has been run on the server)
        self.original_api_key = config.API_KEY
        config.API_KEY = "1234abcd"

        self.hal = RealPcHal()

        # Use an old version to force an update
        self.current_version = "0.0.0"
        self.updater = ota.OTAUpdater(self.hal, self.current_version)

        # Create a temp dir for downloads to avoid clutter
        self.test_dir = os.path.join(os.path.dirname(__file__), 'temp_ota_downloads')
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

        # Change CWD to test dir so files are saved there
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        # Restore config
        config.URL_OTA_VERSION = self.original_url_version
        config.URL_OTA_FILES = self.original_url_files
        config.BASE_URL = self.original_base_url
        config.API_KEY = self.original_api_key

        # Restore CWD
        os.chdir(self.original_cwd)

        # Cleanup temp dir
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_integration_flow(self):
        print("\n=== Starting OTA Integration Test ===")
        print(f"Targeting Server: {config.BASE_URL}")

        # 1. Check for updates
        print("1. Checking for updates...")
        has_update = self.updater.check_for_updates()

        if not has_update:
            print("WARNING: No update found. Ensure server/firmware/latest has files and version > 0.0.0")
            print("Server FW_VERSION might be 0.0.0?")

        self.assertTrue(has_update, "Should find an update available (Server version > 0.0.0)")
        print(f"   Update found: {self.updater.new_version}")

        # 2. Update firmware
        print("2. Downloading firmware...")
        success = self.updater.update_firmware()
        self.assertTrue(success, "Firmware update should succeed")

        # 3. Verify files exist in the temp directory
        print("3. Verifying downloaded files...")

        # Based on what we saw in server/firmware/latest
        expected_files = ["main.py", "ota.py", "hal.py"]

        for f in expected_files:
            exists = os.path.exists(f)
            self.assertTrue(exists, f"File {f} should have been downloaded")
            print(f"   Verified {f} exists")

        print("=== OTA Integration Test Passed ===")

if __name__ == '__main__':
    unittest.main()
