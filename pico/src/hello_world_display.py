# hello_world_display.py
import framebuf
from hal import HardwareAbstractionLayer
import time

# Global rotation setting: 0, 90, 180, 270
ROTATION = 180

def draw_scaled_text(fb, text, x, y, scale=2):
    """Draws larger text by scaling up the 8x8 font."""
    char_buf = bytearray(8)
    char_fb = framebuf.FrameBuffer(char_buf, 8, 8, framebuf.MONO_HLSB)
    for i, char in enumerate(text):
        char_fb.fill(1)
        char_fb.text(char, 0, 0, 0)
        for cy in range(8):
            for cx in range(8):
                if char_fb.pixel(cx, cy) == 0:
                    fb.fill_rect(x + i*8*scale + cx*scale, y + cy*scale, scale, scale, 0)

def rotate_buffer(buf, width, height, angle):
    """Rotates a monochrome buffer by the given angle (software rotation)."""
    if angle == 0:
        return buf

    new_buf = bytearray(len(buf))
    src_fb = framebuf.FrameBuffer(buf, width, height, framebuf.MONO_HLSB)
    dst_fb = framebuf.FrameBuffer(new_buf, width, height, framebuf.MONO_HLSB)
    dst_fb.fill(1) # fill white

    for y in range(height):
        for x in range(width):
            pixel = src_fb.pixel(x, y)
            if angle == 90:
                dst_fb.pixel(height - 1 - y, x, pixel)
            elif angle == 180:
                dst_fb.pixel(width - 1 - x, height - 1 - y, pixel)
            elif angle == 270:
                dst_fb.pixel(y, width - 1 - x, pixel)

    return new_buf

def run():
    hal = HardwareAbstractionLayer()
    epd = hal.get_epd()

    print("Clearing display (Fast/Pretty)...")
    epd.clear(fast=False)

    # 1. Create a "Virtual" buffer to draw on
    width = 200
    height = 200
    buf = bytearray(width * height // 8)
    fb = framebuf.FrameBuffer(buf, width, height, framebuf.MONO_HLSB)
    fb.fill(1)

    # 2. Draw everything normally (as if 0 rotation)
    draw_scaled_text(fb, "Picobell", 10, 40, scale=3)
    draw_scaled_text(fb, "Hello World", 10, 80, scale=2)

    # Bottom-left 'L' (relative to normal orientation)
    fb.line(20, 140, 20, 180, 0)
    fb.line(20, 180, 50, 180, 0)
    fb.rect(2, 2, 196, 196, 0)

    # 3. Rotate the buffer based on your mounting!
    print(f"Applying {ROTATION} degree software rotation...")
    ready_buf = rotate_buffer(buf, width, height, ROTATION)

    print("Updating display (Partial/Fast)...")
    epd.display_partial(ready_buf)

    print("Display updated. Going to sleep...")
    epd.sleep()

if __name__ == "__main__":
    run()
