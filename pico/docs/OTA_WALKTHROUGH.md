# Firmware Upgrade Walkthrough

This guide documents how to test the Firmware Upgrade (OTA) functionality, first locally on your PC, and then on the actual Pico device.

## Prerequisites

- **Server**: Ensure the PHP server is running (`composer start` in `server/`).
- **Database**: The database is seeded using Phinx.
    - Run: `vendor/bin/phinx seed:run -c config/phinx.php -s TestApiKeySeeder` in `server/` to ensure the test API key is present.
- **Python**: Python 3.x installed on your PC.

## Phase 1: Local Integration Test

We have created an integration test `pico/tests/test_ota_integration.py` that simulates the Pico's OTA process on your PC. It hits the local server, downloads files, and verifies them.

### Steps

1.  **Open a terminal** in `pico/`.
2.  **Run the test**:
    ```bash
    python3 tests/test_ota_integration.py
    ```
3.  **Expected Output**:
    ```text
    === Starting OTA Integration Test ===
    Targeting Server: http://localhost:8080
    1. Checking for updates...
    [OTA] Latest version: 0.0.2
    ...
    2. Downloading firmware...
    [OTA] Downloading main.py...
    ...
    [OTA] Update complete. Rebooting...
    3. Verifying downloaded files...
       Verified main.py exists
    === OTA Integration Test Passed ===
    ```

> [!NOTE]
> The test automatically uses the API key `1234abcd` corresponding to the `TestApiKeySeeder`.

---

## Phase 2: Testing on Real Pico

Once the local test passes, you can test on the Pico.

### 1. Preparation

- **Flash Current Code**: Ensure the Pico has the verified `ota.py`, `hal.py`, and `config.py`.
- **Configuration**:
  - Update `pico/src/config.py` (or `wifi.json`) with your Wi-Fi credentials and the **API KEY** (`1234abcd` or your valid key).
  - Update `pico/src/config.py` to point `BASE_URL` to your computer's IP address (e.g., `http://192.168.1.100:8080`), **NOT** localhost. The Pico cannot see `localhost`.

### 2. Triggering Update

You can manually trigger the update via REPL to observe the process.

1.  **Connect to Pico** via USB/UART.
2.  **Open REPL** (e.g., in Thonny or via `mpremote repl`).
3.  **Run the following commands**:

    ```python
    import hal
    import config
    import ota

    # Initialize HAL and Updater
    h = hal.HardwareAbstractionLayer()

    # Connect WiFi explicitly if not done by main.py
    # h.connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD)

    # Initialize with an older version to force update
    updater = ota.OTAUpdater(h, "0.0.0")

    # Check for updates
    if updater.check_for_updates():
        print("Update found! Starting download...")
        updater.update_firmware()
    else:
        print("No update found.")
    ```

### 3. Verification

- Watch the REPL output. It should list the files being downloaded.
- After completion, reset the Pico (`machine.reset()`).
- Verify the new version is running (e.g., check `version.py` or startup logs).

## Troubleshooting

- **"No update found"**:
  - Check if `current_version` passed to `OTAUpdater` is the same as the server version.
  - Check server logs (terminal running `composer start`) for incoming requests.
- **Connection Error**:
  - Ensure `BASE_URL` uses the IP address, not localhost.
  - Ensure PC firewall allows incoming connections on port 8080.
- **Authentication Error** (401):
  - Verify the API Key in `config.py` or `wifi.json` matches the database, ensuring `TestApiKeySeeder` was run if using the test key.
