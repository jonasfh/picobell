import time
import hal
from ble_provision import BLEProvision

def run_test():
    print("--- Picobell BLE Provisioning Hardware Test ---")
    print("Initializing HAL and BLE...")
    hw = hal.HardwareAbstractionLayer()
    prov = BLEProvision(hw)

    print("\nStarting Advertisement...")
    print(f"Device ID: {prov.device_id}")
    print(f"Looking for BLE name: Picobell-{prov.device_id[-4:]}")
    prov.start()

    print("\nWaiting for interactions...")
    print("1. Open 'nRF Connect' app on your phone.")
    print("2. Scan and connect to the Picobell device.")
    print("3. Write to characteristics:")
    print("   - SSID (UUID ends in b1)")
    print("   - Password (UUID ends in b2)")
    print("   - API Key (UUID ends in b5)")
    print("   - Command 'connect' (UUID ends in b3)")
    print("4. Watch the serial console for status updates.")

    start_time = time.time()
    try:
        while not prov.is_provisioned:
            time.sleep(1)
            # Optional: print connection status
            if len(prov._connections) > 0:
                print(f"Central connected. Provisioned: {prov.is_provisioned}", end="\r")
            else:
                print("Advertising...", end="\r")

            # Timeout after 5 minutes for safety (or keep running)
            if time.time() - start_time > 300:
                print("\nTest timeout.")
                break
    except KeyboardInterrupt:
        print("\nTest stopped by user.")

    if prov.is_provisioned:
        print("\n\nSUCCESS! Device provisioned.")
    else:
        print("\nProvisioning not completed.")

if __name__ == "__main__":
    run_test()
