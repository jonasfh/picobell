# hello_world_display.py
import framebuf
from hal import HardwareAbstractionLayer

def draw_scaled_text(fb, text, x, y, scale=2):
    # MicroPython framebuf text is always 8x8.
    # We draw one character at a time to a temporary 8x8 buffer
    # then scale it up using fill_rect.
    char_buf = bytearray(8) # 8x8 monochrome
    char_fb = framebuf.FrameBuffer(char_buf, 8, 8, framebuf.MONO_HLSB)
    for i, char in enumerate(text):
        char_fb.fill(1) # white
        char_fb.text(char, 0, 0, 0) # black
        for cy in range(8):
            for cx in range(8):
                if char_fb.pixel(cx, cy) == 0:
                    fb.fill_rect(x + i*8*scale + cx*scale, y + cy*scale, scale, scale, 0)

def run():
    hal = HardwareAbstractionLayer()
    epd = hal.get_epd()

    print("Clearing display...")
    epd.clear()

    # Create a framebuffer for drawing
    width = 200
    height = 200
    buf = bytearray(width * height // 8)
    fb = framebuf.FrameBuffer(buf, width, height, framebuf.MONO_HLSB)

    # Fill with white
    fb.fill(1)

    # Draw large text
    draw_scaled_text(fb, "Picobell", 5, 40, scale=3)
    draw_scaled_text(fb, "Hello World", 10, 80, scale=2)

    # Draw diagnostic pattern: an "L"
    # Vertical then horizontal. It should look correct in bottom-left.
    fb.line(20, 140, 20, 180, 0)
    fb.line(20, 180, 50, 180, 0)

    # Draw a border
    fb.rect(2, 2, 196, 196, 0)

    print("Updating display...")
    epd.display(buf)

    print("Display updated. Going to sleep...")
    epd.sleep()

if __name__ == "__main__":
    run()
