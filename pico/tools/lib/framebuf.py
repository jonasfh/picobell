# framebuf.py
# A mock for MicroPython's framebuf module for use on desktop (host).
# Includes a Tkinter-based real-time window for UI previewing.

import threading
import time

MONO_VLSB = 0
MONO_HLSB = 1
MONO_HMSB = 2

# Basic 8x8 font for the .text() method
_FONT = {
    ' ': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    'A': (0x00, 0x18, 0x24, 0x42, 0x7E, 0x42, 0x42, 0x00),
    'B': (0x00, 0x7C, 0x22, 0x3C, 0x22, 0x22, 0x7C, 0x00),
    'C': (0x00, 0x3C, 0x42, 0x40, 0x40, 0x42, 0x3C, 0x00),
    'D': (0x00, 0x78, 0x24, 0x22, 0x22, 0x24, 0x78, 0x00),
    'E': (0x00, 0x7E, 0x40, 0x78, 0x40, 0x40, 0x7E, 0x00),
    'F': (0x00, 0x7E, 0x40, 0x78, 0x40, 0x40, 0x40, 0x00),
    'G': (0x00, 0x3C, 0x42, 0x40, 0x4E, 0x42, 0x3C, 0x00),
    'H': (0x00, 0x42, 0x42, 0x7E, 0x42, 0x42, 0x42, 0x00),
    'I': (0x00, 0x3E, 0x08, 0x08, 0x08, 0x08, 0x3E, 0x00),
    'J': (0x00, 0x1E, 0x02, 0x02, 0x02, 0x42, 0x3C, 0x00),
    'K': (0x00, 0x44, 0x48, 0x70, 0x48, 0x44, 0x42, 0x00),
    'L': (0x00, 0x40, 0x40, 0x40, 0x40, 0x40, 0x7E, 0x00),
    'M': (0x00, 0x42, 0x66, 0x5A, 0x42, 0x42, 0x42, 0x00),
    'N': (0x00, 0x42, 0x62, 0x52, 0x4A, 0x46, 0x42, 0x00),
    'O': (0x00, 0x3C, 0x42, 0x42, 0x42, 0x42, 0x3C, 0x00),
    'P': (0x00, 0x7C, 0x42, 0x7C, 0x40, 0x40, 0x40, 0x00),
    'Q': (0x00, 0x3C, 0x42, 0x42, 0x42, 0x4A, 0x3C, 0x02),
    'R': (0x00, 0x7C, 0x42, 0x7C, 0x48, 0x44, 0x42, 0x00),
    'S': (0x00, 0x3C, 0x40, 0x3C, 0x02, 0x02, 0x3C, 0x00),
    'T': (0x00, 0x7E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x00),
    'U': (0x00, 0x42, 0x42, 0x42, 0x42, 0x42, 0x3C, 0x00),
    'V': (0x00, 0x42, 0x42, 0x42, 0x42, 0x24, 0x18, 0x00),
    'W': (0x00, 0x42, 0x42, 0x42, 0x5A, 0x66, 0x42, 0x00),
    'X': (0x00, 0x42, 0x24, 0x18, 0x18, 0x24, 0x42, 0x00),
    'Y': (0x00, 0x42, 0x24, 0x18, 0x08, 0x08, 0x08, 0x00),
    'Z': (0x00, 0x7E, 0x02, 0x04, 0x08, 0x10, 0x7E, 0x00),
    '0': (0x00, 0x3C, 0x46, 0x4A, 0x52, 0x62, 0x3C, 0x00),
    '1': (0x00, 0x08, 0x18, 0x08, 0x08, 0x08, 0x1C, 0x00),
    '2': (0x00, 0x3C, 0x42, 0x04, 0x08, 0x10, 0x7E, 0x00),
    '3': (0x00, 0x3E, 0x02, 0x1C, 0x02, 0x02, 0x3E, 0x00),
    '4': (0x00, 0x08, 0x18, 0x28, 0x48, 0x7E, 0x08, 0x00),
    '5': (0x00, 0x7E, 0x40, 0x7C, 0x02, 0x02, 0x7C, 0x00),
    '6': (0x00, 0x3C, 0x40, 0x7C, 0x42, 0x42, 0x3C, 0x00),
    '7': (0x00, 0x7E, 0x02, 0x04, 0x08, 0x10, 0x20, 0x00),
    '8': (0x00, 0x3C, 0x42, 0x3C, 0x42, 0x42, 0x3C, 0x00),
    '9': (0x00, 0x3C, 0x42, 0x42, 0x3E, 0x02, 0x3C, 0x00),
    '.': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x18),
    ',': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x10),
    ':': (0x00, 0x00, 0x18, 0x18, 0x00, 0x18, 0x18, 0x00),
    '!': (0x00, 0x08, 0x08, 0x08, 0x08, 0x00, 0x08, 0x00),
    '?': (0x00, 0x3C, 0x42, 0x04, 0x08, 0x00, 0x08, 0x00),
    '-': (0x00, 0x00, 0x00, 0x7E, 0x00, 0x00, 0x00, 0x00),
    '_': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x7E, 0x00),
    '+': (0x00, 0x00, 0x08, 0x08, 0x3E, 0x08, 0x08, 0x00),
    '[': (0x00, 0x1C, 0x10, 0x10, 0x10, 0x10, 0x1C, 0x00),
    ']': (0x00, 0x38, 0x08, 0x08, 0x08, 0x08, 0x38, 0x00),
    '(': (0x00, 0x0C, 0x10, 0x10, 0x10, 0x10, 0x0C, 0x00),
    ')': (0x00, 0x30, 0x08, 0x08, 0x08, 0x08, 0x30, 0x00),
}

import queue
try:
    import tkinter as tk
    from PIL import Image, ImageTk
except ImportError:
    tk = None
    Image = None
    ImageTk = None

class EmulatorWindow:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EmulatorWindow, cls).__new__(cls)
                cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        self._initialized = True
        self.root = None
        self.canvas = None
        self.q = queue.Queue()
        self._thread = threading.Thread(target=self._run_tk, daemon=True)
        self._thread.start()

    def _run_tk(self):
        if tk is None:
            print("[Emulator] Tkinter not available.", flush=True)
            return

        print("[Emulator] Initializing Tkinter window...", flush=True)
        try:
            self.root = tk.Tk()
            self.root.title("Picobell EPD Emulator")
            # Blue background to see the window clearly
            self.root.configure(bg="#0000FF")
            self.root.geometry("300x300")

            # Use a Label for the message/image
            self.label = tk.Label(self.root, text="BOOTING...", bg="white", fg="black")
            self.label.place(x=50, y=50, width=200, height=200)

            self.root.update()
            self.root.lift()
            self.root.focus_force()

            self.photo = None

            def poll_queue():
                try:
                    while True:
                        img = self.q.get_nowait()
                        print(f"[Emulator] Received image, rendering...", flush=True)
                        # Always RGB
                        rgb_img = img.convert("RGB")
                        self.photo = ImageTk.PhotoImage(rgb_img)
                        self.label.configure(image=self.photo, text="")
                        self.root.update()
                except queue.Empty:
                    pass
                self.root.after(100, poll_queue)

            self.root.after(100, poll_queue)

            # Simple heartbeat to console
            def heartbeat():
                print("[Emulator] Window is alive...", flush=True)
                self.root.after(2000, heartbeat)
            self.root.after(2000, heartbeat)

            print("[Emulator] Mainloop starting...", flush=True)
            self.root.mainloop()
        except Exception as e:
            print(f"[Emulator] GUI Error: {e}", flush=True)

    def set_image(self, pil_img):
        print(f"[Emulator] Sending image to GUI queue (Mode: {pil_img.mode})")
        self.q.put(pil_img)

class FrameBuffer:
    def __init__(self, buffer, width, height, format=MONO_HLSB):
        self.buffer = buffer
        self.width = width
        self.height = height
        self.format = format

    def pixel(self, x, y, c=None):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return 1 # Default to white/off if out of bounds

        if self.format == MONO_HLSB:
            byte_idx = (y * self.width + x) // 8
            bit_idx = 7 - (x % 8)
            if c is None:
                return (self.buffer[byte_idx] >> bit_idx) & 1
            else:
                if c:
                    self.buffer[byte_idx] |= (1 << bit_idx)
                else:
                    self.buffer[byte_idx] &= ~(1 << bit_idx)
        return 1

    def fill(self, c):
        val = 0xFF if c else 0x00
        for i in range(len(self.buffer)):
            self.buffer[i] = val

    def text(self, text, x, y, c=1):
        for i, char in enumerate(text):
            glyph = _FONT.get(char.upper(), _FONT[' '])
            for gy in range(8):
                row = glyph[gy]
                for gx in range(8):
                    if (row >> (7 - gx)) & 1:
                        self.pixel(x + i*8 + gx, y + gy, c)

    def rect(self, x, y, w, h, c):
        for i in range(x, x + w):
            self.pixel(i, y, c)
            self.pixel(i, y + h - 1, c)
        for j in range(y, y + h):
            self.pixel(x, j, c)
            self.pixel(x + w - 1, j, c)

    def fill_rect(self, x, y, w, h, c):
        for i in range(x, x + w):
            for j in range(y, y + h):
                self.pixel(i, j, c)

    def to_pil(self):
        from PIL import Image
        # Create an 8-bit grayscale image
        img = Image.new("L", (self.width, self.height), 255)
        pixels = img.load()
        for y in range(self.height):
            for x in range(self.width):
                # 0 in framebuf is black, 1 is white.
                # In L mode: 0 is black, 255 is white.
                pixels[x, y] = 255 if self.pixel(x, y) else 0
        return img

    def to_png(self, filename):
        self.to_pil().save(filename)

    def show(self):
        """Display the framebuffer in the live GUI window."""
        win = EmulatorWindow()
        # Ensure the window is ready
        start_time = time.time()
        while not hasattr(win, "label") and time.time() - start_time < 5:
            time.sleep(0.1)
        win.set_image(self.to_pil())
