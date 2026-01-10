
import machine
import time
import config
import hal
from epaper1in54 import EPD

# Setup
hw = hal.HardwareAbstractionLayer()
busy_pin = machine.Pin(config.PIN_EPD_BUSY, machine.Pin.IN)

print(f"Monitoring BUSY pin (GP{config.PIN_EPD_BUSY})...")
print("Initial value:", busy_pin.value())

# Re-init SPI and EPD to use the same pins as main app
spi = hw.create_spi(0, baudrate=4000000,
                     sck_pin=config.PIN_EPD_CLK,
                     mosi_pin=config.PIN_EPD_DIN)
cs = hw.create_pin_out(config.PIN_EPD_CS)
dc = hw.create_pin_out(config.PIN_EPD_DC)
rst = hw.create_pin_out(config.PIN_EPD_RST)

epd = EPD(spi, cs, dc, rst, busy_pin)

def traced_wait(label):
    print(f"--- {label} ---")
    t0 = time.ticks_ms()
    epd.wait_until_idle() # uses our fixed method
    td = time.ticks_diff(time.ticks_ms(), t0)
    print(f"Wait finished. Duration: {td}ms, Final state: {busy_pin.value()}")
    return td

print("Initializing Display...")
epd.init()
traced_wait("Init Wait")

print("Performing Full Refresh (White)...")
image = bytearray([0xFF] * (200 * 200 // 8))
epd.display(image)
duration = traced_wait("Full Display Wait")

if duration < 500:
    print("WARNING: Busy time suspiciously short. Hardware might not have signaled BUSY.")
else:
    print(f"SUCCESS: Hardware signaled BUSY for {duration}ms.")

print("Performing Partial Refresh (Dots Simulation)...")
# Just draw a few dots manually in the buffer
for i in range(10): image[i] = 0x00
epd.display_partial(image)
p_duration = traced_wait("Partial Display Wait")
print(f"Partial duration: {p_duration}ms")

print("Testing Sleep...")
epd.sleep()
print("Done.")
