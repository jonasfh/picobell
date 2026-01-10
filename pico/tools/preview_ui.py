# preview_ui.py
import sys
import os

# Add src and lib to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "lib")))

import hal
from main import DoorbellApp

def generate_previews():
    print("Generating UI Previews...")
    hw = hal.HardwareAbstractionLayer()
    app = DoorbellApp(hw)

    # 1. Start / Listen Mode
    print("-> Preview: LISTEN")
    app.app_mode = "LISTEN"
    app.rotation = 0
    app.last_call_str = "JAN 10 14:30"
    app.display_update()
    os.rename("preview_full.png", "preview_listen.png")

    # 2. Setup Mode
    print("-> Preview: SETUP")
    app.app_mode = "SETUP"
    app.rotation = 0 # Easier to see in previews
    app.display_update()
    os.rename("preview_full.png", "preview_setup.png")

    # 2b. Setup Saved
    print("-> Preview: SETUP SAVED")
    fb, buf = app._get_fb()
    app.draw_scaled_text(fb, "PICOBELL", 10, 15, scale=3)
    fb.rect(2, 2, 196, 196, 0)
    app.draw_setup_screen(fb, status="SAVED")
    app._rotate_and_display(fb, buf)
    os.rename("preview_full.png", "preview_setup_saved.png")

    # 3. Open Mode
    print("-> Preview: OPEN")
    app.app_mode = "OPEN"
    app.display_update()
    os.rename("preview_full.png", "preview_open.png")

    # 4. OTA Update Mode
    print("-> Preview: OTA")
    app.display_ota_progress(5, 10)
    # display_ota_progress uses display_partial for current > 1
    if os.path.exists("preview_partial.png"):
        os.rename("preview_partial.png", "preview_ota.png")
    elif os.path.exists("preview_full.png"):
        os.rename("preview_full.png", "preview_ota.png")

if __name__ == "__main__":
    generate_previews()
    print("Done. Check preview_*.png files.")
