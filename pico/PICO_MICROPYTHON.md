# Installing MicroPython on Raspberry Pi Pico W

## Overview

This guide explains how to flash the newest MicroPython firmware onto a Pico W.

---

## Requirements

* Raspberry Pi Pico W
* USB cable
* A computer (Windows, macOS, Linux)

---

## Steps

### 1. Download the latest firmware

Go to:

[https://micropython.org/download/rp2-picow/](https://micropython.org/download/rp2-picow/)

Download the newest `.uf2` file, for example:
micropython-1.25.0-picow.uf2

---

### 2. Put Pico in bootloader mode

1. Hold the **BOOTSEL** button
2. Plug in the USB cable
3. Release the button

A disk named `RPI-RP2` appears.

---

### 3. Flash MicroPython

Drag the `.uf2` file onto the `RPI-RP2` drive.

The Pico reboots automatically into MicroPython.

---

### 4. Verify installation

Open Thonny or any serial terminal and run:

```python
import sys
sys.implementationYou should see MicroPython 1.22+
```
