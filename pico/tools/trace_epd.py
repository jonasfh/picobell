
import machine
import time
import config

# Setup Busy pin as it is on the Pico
busy = machine.Pin(config.PIN_EPD_BUSY, machine.Pin.IN)

print("Monitoring BUSY pin (GP10)...")
print("Initial value:", busy.value())

# Let's try to trigger a refresh via mpremote or just observe.
# Actually, I can use the HAL and EPD classes to trigger a refresh.
import hal
from epaper1in54 import EPD

hw = hal.HardwareAbstractionLayer()
# We need to manually initialize EPD if we want to trace it
spi = hw.create_spi(0, baudrate=4000000,
                     sck_pin=config.PIN_EPD_CLK,
                     mosi_pin=config.PIN_EPD_DIN)
cs = hw.create_pin_out(config.PIN_EPD_CS)
dc = hw.create_pin_out(config.PIN_EPD_DC)
rst = hw.create_pin_out(config.PIN_EPD_RST)
busy_pin = hw.create_pin_in(config.PIN_EPD_BUSY, pull_up=False)

epd = EPD(spi, cs, dc, rst, busy_pin)

def traced_wait():
    print("Waiting for idle...")
    t0 = time.ticks_ms()
    # Check if it's already busy or if it takes time to transition
    time.sleep_ms(50)
    count = 0
    while busy_pin.value() == 1:
        count += 1
        time.sleep_ms(10)
    td = time.ticks_diff(time.ticks_ms(), t0)
    print(f"Finished waiting. State: {busy_pin.value()}, Time: {td}ms, Iterations: {count}")

print("Initializing EPD...")
epd.init()
traced_wait()

print("Sending blank image...")
image = bytearray([0xFF] * (200 * 200 // 8))
epd.display(image)
traced_wait()

print("Entering sleep...")
epd.sleep()
print("Done.")
