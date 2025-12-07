markdown=<<'EOF'

# Developing for Pico W Using Thonny

## Overview

Thonny provides the simplest workflow for editing and uploading files to the
MicroPython device. This guide covers installing, configuring, and working
around common environment issues.

---

## Install Thonny

### Recommended

Install Thonny using Python 3.11:

`python3.11 -m pip install thonny`

Thonny often fails on distro-packaged Python builds. A venv keeps it stable.

---

## Running Thonny from a virtualenv

```bash
    python3.11 -m venv venv
    source venv/bin/activate
    pip install thonny
    thonny
```

This avoids issues with older GTK libraries and plugin mismatches.

---

## Configure Interpreter

Inside Thonny:

Tools → Options → Interpreter

Select:

MicroPython (Raspberry Pi Pico)

Choose the serial port corresponding to the Pico.

---

## Show File Browser

If you don’t see the device files:

View → Files

Two panes appear: local and device.

---

## Upload Files

Right-click a local file → choose:

Upload to /

or use:

File → Save copy to → MicroPython device

---

## Autostart main.py

MicroPython automatically runs:

1. `boot.py` (optional)
2. `main.py` (on every boot)

Place your app logic in `main.py`.

---

## Common Problems

### Thonny doesn’t detect the Pico

* Ensure you’re not using USB hubs
* Try another cable
* Reflash MicroPython

### Write errors

The Pico’s flash can fill up quickly. Delete old files in the device panel.
