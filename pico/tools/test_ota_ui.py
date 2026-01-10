
import hal
import main
import time

hw = hal.HardwareAbstractionLayer()
app = main.DoorbellApp(hw)

print("Simulating OTA Update UI (Dots)...")

# 1. Start update (Full Refresh)
print("Step 1/5: Initial Full Refresh")
app.display_ota_progress(1, 5, False)

# 2. Progress (Partial)
for i in range(2, 5):
    print(f"Step {i}/5: Partial Refresh")
    time.sleep(1) # Faster than real download to test responsiveness
    app.display_ota_progress(i, 5, False)

# 3. Done (Full Refresh + Reboot)
print("Step 5/5: Final Refresh + Sleep")
time.sleep(1)
app.display_ota_progress(5, 5, True)

print("UI Simulation Done.")
