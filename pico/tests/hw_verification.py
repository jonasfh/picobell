# tests/test_hw.py
# This script is intended to be run ON THE PICO via mpremote
import machine
import time
import sys

# Constants to match config (manually copied or imported if deployed)
PIN_RING_IN = 10
PIN_DOOR_OUT = 11
PIN_LED = "LED"

def test_hardware():
    print("--- Hardware Verification Test ---")
    
    # 1. Test LED
    print("[TEST] Toggling LED...")
    led = machine.Pin(PIN_LED, machine.Pin.OUT)
    for _ in range(5):
        led.toggle()
        time.sleep(0.2)
    led.off()
    print("[PASS] LED toggled (visual check required)")

    # 2. Test Door Output
    print(f"[TEST] Testing Door Output on Pin {PIN_DOOR_OUT}")
    door = machine.Pin(PIN_DOOR_OUT, machine.Pin.OUT)
    door.off()
    
    # Pulse
    print("       Pulsing HIGH for 1s...")
    door.on()
    time.sleep(1)
    door.off()
    print("[PASS] Door output pulsed (check with multimeter/LED)")

    # 3. Test Ring Input
    print(f"[TEST] Testing Ring Input on Pin {PIN_RING_IN}")
    ring = machine.Pin(PIN_RING_IN, machine.Pin.IN, machine.Pin.PULL_UP)
    
    print("       Waiting for signal (Connect Pin 10 to GND)... Timeout 10s")
    t0 = time.time()
    detected = False
    while time.time() - t0 < 10:
        if ring.value() == 0:
            print("       Signal DETECTED!")
            detected = True
            break
        time.sleep(0.1)
        
    if detected:
        print("[PASS] Ring Input Detected")
    else:
        print("[FAIL] Ring Input NOT Detected (Did you bridge the pin?)")

    print("--- Test Complete ---")

if __name__ == "__main__":
    test_hardware()
