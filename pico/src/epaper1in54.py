# epaper1in54.py
"""
Waveshare 1.54" E-Ink Display (V2) Driver for MicroPython (SSD1681)

--- HOW E-INK SCREENS WORK ---
E-ink screens use "electrophoretic" technology. Tiny capsules containing charged
black and white pigments move when an electric field is applied.
- PROS: High contrast, reads like paper, consumes ZERO power when static.
- CONS: Slow refresh (1-2s), "ghosting" if not fully refreshed.

--- SPI PROTOCOL (Serial Peripheral Interface) ---
This driver uses 4-wire SPI:
1. CS (Chip Select): Pin stays LOW during communication.
2. SCLK (Serial Clock): Synchronizes data transfer.
3. DIN/MOSI: The data being sent from the Pico to the Screen.
4. DC (Data/Command): Tells the screen if the incoming byte is a code (LOW)
   or image data (HIGH).
"""

import time

# Display resolution
EPD_WIDTH       = 200
EPD_HEIGHT      = 200

class EPD:
    def __init__(self, spi, cs, dc, rst, busy):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT

    def _command(self, command, data=None):
        """Sends a command byte, optionally followed by data bytes."""
        self.dc.off()
        self.cs.off()
        self.spi.write(bytearray([command]))
        self.cs.on()
        if data is not None:
            self._data(data)

    def _data(self, data):
        """Sends one or more data bytes."""
        self.dc.on()
        self.cs.off()
        if isinstance(data, int):
            self.spi.write(bytearray([data]))
        else:
            self.spi.write(data)
        self.cs.on()

    def wait_until_idle(self):
        """Busy pin is HIGH when screen is processing. We wait a bit for it to transition."""
        time.sleep(0.1)
        while self.busy.value() == 1:
            time.sleep(0.01)

    def reset(self):
        """Hardware reset pulse."""
        self.rst.on()
        time.sleep(0.1)
        self.rst.off()
        time.sleep(0.01)
        self.rst.on()
        time.sleep(0.1)

    def set_ram_address(self, x, y):
        """Sets the internal memory pointer to (x, y)."""
        self._command(0x4E, x & 0xFF)
        self._command(0x4F)
        self._data(bytearray([y & 0xFF, (y >> 8) & 0xFF]))

    def init(self):
        """Standard V2 Initialization sequence."""
        self.reset()
        self.wait_until_idle()

        self._command(0x12) # Soft Reset
        self.wait_until_idle()

        # Driver output control: Sets mux and scan direction
        self._command(0x01, bytearray([0xC7, 0x00, 0x00]))

        # Data entry mode: 0x03 = X-increment, Y-increment
        self._command(0x11, 0x03)

        # RAM Ranges
        self._command(0x44, bytearray([0x00, 0x18])) # X: 0 to 24 (25*8=200px)
        self._command(0x45, bytearray([0x00, 0x00, 0xC7, 0x00])) # Y: 0 to 199

        self._command(0x3C, 0x01) # Border waveform
        self._command(0x18, 0x80) # Internal temp sensor

        self.set_ram_address(0, 0)
        self.wait_until_idle()

    def display(self, image):
        """Pushes a full framebuffer to the screen and triggers a full refresh."""
        if image is None: return
        self.set_ram_address(0, 0)
        self._command(0x24, image)

        self._command(0x22, 0xF7)
        self._command(0x20)
        self.wait_until_idle()

    def display_partial(self, image):
        """Triggers a partial refresh (SSD1681 DISPLAY Mode 2)."""
        if image is None: return
        self.set_ram_address(0, 0)
        self._command(0x24, image)

        # 0xFF = DISPLAY Mode 2 (Partial/Fast Update)
        self._command(0x22, 0xFF)
        self._command(0x20)
        self.wait_until_idle()

    def _write_ram_all(self, value):
        """Helper to fill both RAM banks with a single value."""
        self.set_ram_address(0, 0)
        self._command(0x24)
        chunk = bytearray([value] * 200)
        self.dc.on()
        self.cs.off()
        for _ in range(25 * 200 // 200):
            self.spi.write(chunk)
        self.cs.on()

        # Some displays need the second RAM bank (0x26) cleared to avoid red tints
        self.set_ram_address(0, 0)
        self._command(0x26)
        self.dc.on()
        self.cs.off()
        for _ in range(25 * 200 // 200):
            self.spi.write(chunk)
        self.cs.on()

    def clear(self, fast=False):
        """Clears display. Set fast=True for partial/no-flicker update."""
        self._write_ram_all(0xFF) # Fill with White

        if fast:
            self._command(0x22, 0xFF) # Partial Update Mode
        else:
            self._command(0x22, 0xF7) # Full Update Mode

        self._command(0x20)
        self.wait_until_idle()

    def sleep(self):
        """Enters Deep Sleep mode to save power."""
        self._command(0x10, 0x01)
