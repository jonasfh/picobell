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
        """Busy pin is HIGH when screen is processing."""
        while self.busy.value() == 1:
            time.sleep(0.05)

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
        # [0.0.6-note] Hardware flips (GD/TB) often cause mirroring issues.
        # We use default scan and will handle rotation in software if needed.
        self._command(0x01, bytearray([0xC7, 0x00, 0x00]))

        # Data entry mode:
        # 0x03 = X-increment, Y-increment
        self._command(0x11, 0x03)

        # RAM Ranges
        self._command(0x44, bytearray([0x00, 0x18])) # X: 0 to 24 (25*8=200px)
        self._command(0x45, bytearray([0x00, 0x00, 0xC7, 0x00])) # Y: 0 to 199

        self._command(0x3C, 0x01) # Border waveform
        self._command(0x18, 0x80) # Internal temp sensor

        self.set_ram_address(0, 0)
        self.wait_until_idle()

    def display(self, image):
        """Pushes a full framebuffer to the screen and triggers refresh."""
        if image is None: return
        self.set_ram_address(0, 0)
        self._command(0x24, image) # Write 'Black' RAM

        self._command(0x22, 0xF7) # Update Control: Load sequence
        self._command(0x20)       # Master Activation (The actual blink)
        self.wait_until_idle()

    def clear(self):
        """Optimized: Writes white (0xFF) to the entire display memory."""
        self.set_ram_address(0, 0)
        self._command(0x24)

        # We push one large chunk instead of many tiny bits
        white_chunk = bytearray([0xFF] * 200) # One row at a time (effectively)
        self.dc.on()
        self.cs.off()
        for _ in range(25 * 200 // 200): # 25 bytes per row * 200 rows
            self.spi.write(white_chunk)
        self.cs.on()

        self._command(0x22, 0xF7)
        self._command(0x20)
        self.wait_until_idle()

    def sleep(self):
        """Enters Deep Sleep mode to save power (0.01uA)."""
        self._command(0x10, 0x01)
