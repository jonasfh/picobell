# BLE Provisioning Testing Walkthrough

This guide explains how to verify the BLE provisioning flow of the Picobell Pico
W firmware. We provide two methods: a local mock-driven test for fast
development and a hardware-compatible script for actual on-device verification.

## 1. Local Integration Testing (No Pico Required)

The local test environment uses a mock of the MicroPython `bluetooth` and
`network` stacks to simulate the provisioning process on your development
machine.

### Prerequisites
- Python 3.10+ installed locally.

### Running the Test
Execute the following command from the project root:

```bash
python3 pico/tests/test_ble_mock.py
```

### What is verified:
- **Device Identification**: Generation of the unique `Picobell-XXXX` name based
    on the MAC address.
- **Protocol Handling**: Correct parsing of BLE write events for SSID, Password,
    and API Key.
- **State Machine**: Verification that the `connect` command triggers the WiFi
    connection logic.
- **Persistence**: Ensuring credentials are correctly formatted for storage in
    `/flash/wifi.json`.

---

## 2. Hardware Verification (On Pico W)

To test the real BLE stack on the physical hardware, use the following steps.

### Prerequisites
- Pico W with MicroPython installed.
- A BLE scanner app on your phone (e.g.,
    [nRF Connect](https://www.nordicsemi.com/Products/Development-tools/nRF-Connect-for-mobile)).

### Steps
1. **Flash Source**: Ensure `pico/src/ble_provision.py` is on the Pico.
2. **Flash Test Script**: Upload [pico/tests/test_ble_hardware.py](../tests/test_ble_hardware.py) to the Pico.
3. **Run Test**: Execute `test_ble_hardware.py` (e.g., via Thonny or `mpremote`).
4. **Interact**:
    - Open **nRF Connect** and scan for `Picobell-XXXX`.
    - Connect to the device.
    - Write your WiFi SSID to the SSID characteristic.
    - Write your WiFi Password to the Password characteristic.
    - Write `connect` to the Command characteristic.
5. **Observe**: The Pico serial console will show the provisioning status.

---

## Testing Infrastructure

The following internal files support this testing:
- [test_ble_mock.py](../tests/test_ble_mock.py):
    The main local test runner.
- [bluetooth_mock.py](../tests/bluetooth_mock.py):
    Simulates the MicroPython `bluetooth` module behavior.
- [network_mock.py](../tests/network_mock.py):
    Simulates the `network.WLAN` behavior including status notifications.
- [micropython_mock.py](../tests/micropython_mock.py):
    Helper for `const()` and other MicroPython-specific built-ins.
