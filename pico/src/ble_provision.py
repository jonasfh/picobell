# ble_provision.py
# BLE provisioning service for Picobell Pico W
from micropython import const
import bluetooth
import time

FLAG_READ = const(0x02)
FLAG_WRITE = const(0x08)
FLAG_WRITE_NR = const(0x10)
FLAG_NOTIFY = const(0x10)

UUID_DEV_INFO = bluetooth.UUID("12345678-1234-1234-1234-1234567890a0")
UUID_DEV_ID   = bluetooth.UUID("12345678-1234-1234-1234-1234567890a1")
UUID_FW       = bluetooth.UUID("12345678-1234-1234-1234-1234567890a2")

UUID_WIFI     = bluetooth.UUID("12345678-1234-1234-1234-1234567890b0")
UUID_SSID     = bluetooth.UUID("12345678-1234-1234-1234-1234567890b1")
UUID_PASS     = bluetooth.UUID("12345678-1234-1234-1234-1234567890b2")
UUID_CMD      = bluetooth.UUID("12345678-1234-1234-1234-1234567890b3")
UUID_STATUS   = bluetooth.UUID("12345678-1234-1234-1234-1234567890b4")
UUID_API_KEY  = bluetooth.UUID("12345678-1234-1234-1234-1234567890b5")


def adv_payload(name=None, services=None):
    p = bytearray()

    def _append(typ, val):
        p.extend(bytes((len(val) + 1, typ)))
        p.extend(val)

    if name:
        _append(0x09, name.encode())

    if services:
        for uuid in services:
            # konverter UUID til bytes
            b = uuid.uuid if hasattr(uuid, "uuid") else uuid
            if isinstance(b, int):  # 16-bit UUID
                b = b.to_bytes(2, "little")
            elif isinstance(b, bluetooth.UUID):  # noen UUID-objekter
                b = bytes(b)
            # nå er b bytes
            if len(b) == 2:
                _append(0x02, b)
            elif len(b) == 16:
                _append(0x06, b)
            else:
                raise ValueError("Unsupported UUID length")

    return p



class BLEProvision:
    is_provisioned = False  # Indicates if provisioning is done

    def __init__(self, hal):
        self.hal = hal
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.ble.irq(self._irq)

        self._connections = set()
        self._ssid = ""
        self._pwd = ""
        self._api_key = ""

        self.device_id = self.hal.get_mac_address()

        devinfo = (UUID_DEV_INFO,
                   ((UUID_DEV_ID, FLAG_READ,),
                    (UUID_FW, FLAG_READ,),))

        wifisrv = (UUID_WIFI,
                   ((UUID_SSID, FLAG_WRITE,),
                    (UUID_PASS, FLAG_WRITE,),
                    (UUID_API_KEY, FLAG_WRITE,),
                    (UUID_CMD, FLAG_WRITE,),
                    (UUID_STATUS, FLAG_NOTIFY,),))

        services = (devinfo, wifisrv)
        handles = self.ble.gatts_register_services(services)

        print("Device id: ", self.device_id)
        (devinfo_handles, wifisrv_handles) = handles
        (self.h_dev_id, self.h_fw) = devinfo_handles
        (self.h_ssid, self.h_pwd,
         self.h_api, self.h_cmd,
         self.h_stat) = wifisrv_handles

        # Increase buffers for long strings (like API Keys or long Passwords)
        # Default is 20 bytes, which causes truncation.
        self.ble.gatts_set_buffer(self.h_ssid, 64)
        self.ble.gatts_set_buffer(self.h_pwd, 64)
        self.ble.gatts_set_buffer(self.h_api, 256) # API keys can be quite long

        self.ble.gatts_write(self.h_dev_id, self.device_id)
        from version import FW_VERSION
        self.ble.gatts_write(self.h_fw, FW_VERSION)


    def start(self):
        name = "Picobell-" + self.device_id[-4:]
        payload = adv_payload(name=name, services=[UUID_WIFI])
        self.ble.config(gap_name=name)
        self.ble.gap_advertise(100_000, payload)
        scan_resp = adv_payload(name=name)
        self.ble.gap_advertise(100_000, adv_data=payload, resp_data=scan_resp)

    def _irq(self, event, data):
        IRQ_CENTRAL_CONNECT    = 1
        IRQ_CENTRAL_DISCONNECT = 2
        IRQ_GATTS_WRITE        = 3

        print("IRQ event:", event, "data:", data)

        if event == IRQ_CENTRAL_CONNECT:
            self._connections.add(data[0])
            print("Connected to central", data[0])
        elif event == IRQ_CENTRAL_DISCONNECT:
            self._connections.remove(data[0])
            print("Disconnected from central", data[0])
            self.start()
        elif event == IRQ_GATTS_WRITE:
            print("Write to handle", data[1])
            self._write(data[1])

    def _write(self, h):
        print("Writing to handle:", h)
        if h == self.h_ssid:
            raw = self.ble.gatts_read(h)
            # If the SSID is written multiple times, it's either chunks or a retry.
            # Standard BLE Write Request starts at offset 0.
            # But here the app is chunking, so we append.
            self._ssid += raw.decode()
            print("SSID appended:", self._ssid)
        elif h == self.h_pwd:
            raw = self.ble.gatts_read(h)
            self._pwd += raw.decode()
            print("Password appended (len={})".format(len(self._pwd)))
        elif h == self.h_api:
            raw = self.ble.gatts_read(h)
            self._api_key += raw.decode()
            print(f"API Key appended (total len={len(self._api_key)})")
        elif h == self.h_cmd:
            cmd = self.ble.gatts_read(h).decode()
            print("CMD received:", cmd)
            if cmd == "connect":
                self._connect()

    def _notify(self, msg):
        for c in self._connections:
            self.ble.gatts_notify(c, self.h_stat, msg)

    def _connect(self):
        print("Connecting?")
        self._notify("connecting")

        success = self.hal.connect_wifi(self._ssid, self._pwd)

        if success:
            # We don't have a direct way to get IP from hal.connect_wifi currently
            # but we can assume it works or add a way to get it.
            # Actually hal.connect_wifi already prints "Wi-Fi Connected" on host.
            # On real Pico it uses network.WLAN.
            # Let's see if we can get IP.
            # I will assume IP is available via some method if needed, but for now:
            self._notify("connected:OK")

            cfg = {"ssid": self._ssid,
                   "pwd": self._pwd,
                   "device_api_key": self._api_key}

            self.hal.save_json("/flash/wifi.json", cfg)
            self.is_provisioned = True
        else:
            self._notify("failed")
