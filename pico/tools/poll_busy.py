
import machine
import time
import config
import hal
from epaper1in54 import EPD

# Setup
hw = hal.HardwareAbstractionLayer()
busy_pin = machine.Pin(config.PIN_EPD_BUSY, machine.Pin.IN)

spi = hw.create_spi(0, baudrate=4000000,
                     sck_pin=config.PIN_EPD_CLK,
                     mosi_pin=config.PIN_EPD_DIN)
cs = hw.create_pin_out(config.PIN_EPD_CS)
dc = hw.create_pin_out(config.PIN_EPD_DC)
rst = hw.create_pin_out(config.PIN_EPD_RST)

epd = EPD(spi, cs, dc, rst, busy_pin)

print("Triggering refresh and polling GP10 for 5 seconds...")
epd.init()
image = bytearray([0x00] * (200 * 200 // 8)) # All black
epd.set_ram_address(0, 0)
epd._command(0x24, image)
epd._command(0x22, 0xF7)
epd._command(0x20)

t0 = time.ticks_ms()
states = []
while time.ticks_diff(time.ticks_ms(), t0) < 5000:
    states.append(busy_pin.value())
    time.sleep_ms(10)

# Compress states for printing
comp = []
if states:
    curr = states[0]
    count = 1
    for i in range(1, len(states)):
        if states[i] == curr:
            count += 1
        else:
            comp.append((curr, count))
            curr = states[i]
            count = 1
    comp.append((curr, count))

print("State transitions (Value, Samples):", comp)
