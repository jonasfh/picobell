# live_demo.py
import sys
import os
import time

# Add src and lib to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "lib")))

import hal
from main import DoorbellApp

def run_live_demo():
    print("Starting Live Demo...")
    print("The emulator window should appear shortly.")

    hw = hal.HardwareAbstractionLayer()
    app = DoorbellApp(hw)

    # 0. Initial Refresh
    app.display_update()
    time.sleep(1)

    # 1. Boot sequence
    print("Step 1: Booting")
    app.app_mode = "START"
    app.display_update()
    time.sleep(2)

    # 2. Listen Mode
    print("Step 2: Listen Mode")
    app.app_mode = "LISTEN"
    app.last_call_str = "IDLE..."
    app.display_update()
    time.sleep(2)

    # 3. Simulate Ring
    print("Step 3: Ring Event")
    app.last_call_str = "15:30 (NEW)"
    app.display_update()
    time.sleep(3)

    # 4. Open Door
    print("Step 4: Opening Door")
    app.app_mode = "OPEN"
    app.display_update()
    time.sleep(3)

    # 5. Back to Listen
    print("Step 5: Back to Listen")
    app.app_mode = "LISTEN"
    app.display_update()
    time.sleep(2)

    # 6. Enter Setup
    print("Step 6: Setup Mode")
    app.app_mode = "SETUP"
    app.display_update()
    time.sleep(4)

    # 7. Setup Success
    print("Step 7: Setup Successful")
    fb, buf = app._get_fb()
    app.draw_scaled_text(fb, "PICOBELL", 10, 15, scale=3)
    fb.rect(2, 2, 196, 196, 0)
    app.draw_setup_screen(fb, status="SAVED")
    app._rotate_and_display(fb, buf)
    time.sleep(4)

    # 8. OTA Progress
    print("Step 8: OTA Update")
    for i in range(1, 11):
        app.display_ota_progress(i, 10, is_done=(i==10))
        time.sleep(0.5)

    print("Demo Finished. The window will close in 5 seconds.")
    time.sleep(5)

if __name__ == "__main__":
    try:
        run_live_demo()
    except KeyboardInterrupt:
        print("\nExiting...")
