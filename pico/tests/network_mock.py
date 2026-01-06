# network_mock.py
STA_IF = 0

class WLAN:
    def __init__(self, interface):
        self.interface = interface
        self._active = False
        self._connected = False
        self._ssid = None
        self._pwd = None

    def active(self, val=None):
        if val is not None:
            self._active = val
        return self._active

    def connect(self, ssid, pwd):
        self._ssid = ssid
        self._pwd = pwd
        print(f"[WLAN MOCK] Connecting to {ssid}...")
        # In mock, we auto-connect after a simulator-defined delay or immediately
        self._connected = True

    def disconnect(self):
        self._connected = False

    def isconnected(self):
        return self._connected

    def ifconfig(self):
        return ("192.168.1.100", "255.255.255.0", "192.168.1.1", "8.8.8.8")

    def config(self, param):
        if param == "mac":
            return b"\x00\x11\x22\x33\x44\x55"
        return None
