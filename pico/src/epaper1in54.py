# epaper1in54.py
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

    def _command(self, command):
        self.dc.off()
        self.cs.off()
        self.spi.write(bytearray([command]))
        self.cs.on()

    def _data(self, data):
        self.dc.on()
        self.cs.off()
        self.spi.write(bytearray([data]))
        self.cs.on()

    def wait_until_idle(self):
        while self.busy.value() == 1:
            time.sleep(0.1)

    def reset(self):
        self.rst.on()
        time.sleep(0.2)
        self.rst.off()
        time.sleep(0.01)
        self.rst.on()
        time.sleep(0.2)

    def init(self):
        self.reset()
        self.wait_until_idle()

        self._command(0x12) # Soft Reset
        self.wait_until_idle()

        # Adjusted Driver output control: TB=1 flips the screen vertically
        self._command(0x01)
        self._data(0xC7)
        self._data(0x00)
        self._data(0x04) # TB=1, SM=0, GD=0

        self._command(0x11) # Data entry mode
        self._data(0x03)    # X inc, Y inc, X-mode

        self._command(0x44) # Set Ram-X address start/end position
        self._data(0x00)
        self._data(0x18)    # 0x18-->(24+1)*8=200

        self._command(0x45) # Set Ram-Y address start/end position
        self._data(0x00)
        self._data(0x00)
        self._data(0xC7)    # 0xC7-->(199+1)=200
        self._data(0x00)

        self._command(0x3C) # BorderWavefrom
        self._data(0x01)

        self._command(0x18) # Temperature Sensor Control
        self._data(0x80)

        self.set_ram_address(0, 0)
        self.wait_until_idle()

    def set_ram_address(self, x, y):
        self._command(0x4E) # Set RAM x address count
        self._data(x & 0xFF)
        self._command(0x4F) # Set RAM y address count
        self._data(y & 0xFF)
        self._data((y >> 8) & 0xFF)

    def display(self, image):
        if image is None:
            return

        self.set_ram_address(0, 0)
        self._command(0x24)
        for i in range(0, len(image)):
            self._data(image[i])

        self._command(0x22) # Display Update Control 2
        self._data(0xF7)
        self._command(0x20) # Master Activation
        self.wait_until_idle()

    def clear(self):
        self.set_ram_address(0, 0)
        self._command(0x24)
        for i in range(0, int(EPD_WIDTH * EPD_HEIGHT / 8)):
            self._data(0xFF)

        self._command(0x22) # Display Update Control 2
        self._data(0xF7)
        self._command(0x20) # Master Activation
        self.wait_until_idle()

    def sleep(self):
        self._command(0x10) # Deep sleep mode
        self._data(0x01)
