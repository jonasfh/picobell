# UI Development with Screen Emulator

Since testing on the physical 200x200px E-Ink screen is time-consuming, you can use the built-in screen emulator to design and verify layouts on your PC.

## Architecture

The emulator works by providing a desktop-compatible mock for MicroPython's hardware-specific modules:

- **`hal.py`**: Automatically detects if it's running on a PC (non-MicroPython). If so, it uses `MockEPD`.
- **`MockEPD`**: Instead of sending SPI commands to a physical screen, it renders the framebuffer to a `.png` file.
- **`framebuf.py` (mock)**: Located in `pico/tools/lib/`, this provides a pure-python implementation of the `framebuf` drawing primitives (lines, rectangles, text) and can export its contents to PNG using the **Pillow** library.

## Getting Started

### 1. Prerequisites
Ensure you have the Pillow library installed on your development machine:
```bash
pip3 install Pillow
```

### 2. Live Demo
To see the UI in action with real-time updates and transitions, run the live demo script:
```bash
/home/jonas/dev/android-picobell/pico/venv/bin/python3 pico/tools/live_demo.py
```
This will open a Tkinter window and cycle through various app states (Boot, Listen, Ring, Open, Setup, OTA).

### 3. Generating Static Previews
If you just need a quick set of PNG files for documentation or sharing:
```bash
/home/jonas/dev/android-picobell/pico/venv/bin/python3 pico/tools/preview_ui.py
```
This creates `preview_listen.png`, `preview_setup.png`, etc., in the project root.

## How to Develop a New Screen

### 1. Define a Drawing Method
In `pico/src/main.py`, add a new method to the `DoorbellApp` class:

```python
def draw_my_new_screen(self, fb):
    # Use standard framebuf drawing commands
    self.draw_scaled_text(fb, "HELLO WORLD", 10, 50, scale=2)
    fb.rect(10, 80, 180, 40, 0)
```

### 2. Update `display_update`
Add your new mode to the switch in `display_update`:

```diff
     def display_update(self, partial=False):
         fb, buf = self._get_fb()
         ...
         if self.app_mode == "LISTEN":
             self.draw_listen_screen(fb)
+        elif self.app_mode == "MY_NEW_MODE":
+            self.draw_my_new_screen(fb)
```

### 3. Add to `preview_ui.py`
To see your changes immediately, add a block to `pico/tools/preview_ui.py`:

```python
    print("-> Preview: MY NEW MODE")
    app.app_mode = "MY_NEW_MODE"
    app.display_update()
    os.rename("preview_full.png", "preview_new_mode.png")
```

## Pro Tips
- **Rotation**: The emulator supports the 180-degree rotation used in the physical mount. For easier debugging in the CLI, the preview script often sets `app.rotation = 0`.
- **Scaling**: Use `draw_scaled_text` for readable fonts. The standard MicroPython 8x8 font is quite small on a high-density E-Ink screen.
- **Partial Refreshes**: `epd.display_partial` in the mock will save as `preview_partial.png`, helping you distinguish between full and partial update flows.
