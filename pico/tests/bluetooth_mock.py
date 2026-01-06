# bluetooth_mock.py
class UUID:
    def __init__(self, uuid):
        if isinstance(uuid, str):
            # Convert hex string (with dashes) to bytes
            self._bytes = bytes.fromhex(uuid.replace("-", ""))
        elif isinstance(uuid, int):
            self._bytes = uuid.to_bytes(2, "little")
        else:
            self._bytes = bytes(uuid)

    def __bytes__(self):
        return self._bytes

    def __repr__(self):
        return f"UUID({self._bytes.hex()})"

class BLE:
    def __init__(self):
        self._active = False
        self._irq_handler = None
        self._attrs = {}
        self._gap_name = ""
        self._adv_data = None
        self._resp_data = None

    def active(self, val=None):
        if val is not None:
            self._active = val
        return self._active

    def irq(self, handler):
        self._irq_handler = handler

    def gatts_register_services(self, services):
        # Simply return a set of integer handles
        # In real BLE, it's complex, but for testing we just need identifiers
        # structure: ( (UUID, ( (charUUID, flags), ... )), ... )
        handles = []
        h_counter = 1
        for srv_uuid, chars in services:
            char_handles = []
            for char_uuid, flags in chars:
                char_handles.append(h_counter)
                self._attrs[h_counter] = b""
                h_counter += 1
            handles.append(tuple(char_handles))
        return tuple(handles)

    def gatts_read(self, handle):
        return self._attrs.get(handle, b"")

    def gatts_write(self, handle, data):
        if isinstance(data, str):
            data = data.encode()
        self._attrs[handle] = data

    def gatts_notify(self, conn_handle, char_handle, data):
        if isinstance(data, str):
            data = data.encode()
        print(f"[BLE MOCK] Notify on conn {conn_handle}, char {char_handle}: {data}")

    def config(self, gap_name=None):
        if gap_name:
            self._gap_name = gap_name

    def gap_advertise(self, interval_us, adv_data=None, resp_data=None):
        self._adv_data = adv_data
        self._resp_data = resp_data

    # Helper for testing
    def simulate_write(self, conn_handle, char_handle, data):
        self.gatts_write(char_handle, data)
        if self._irq_handler:
            self._irq_handler(3, (conn_handle, char_handle)) # IRQ_GATTS_WRITE = 3

    def simulate_connect(self, conn_handle, addr_type, addr):
        if self._irq_handler:
            self._irq_handler(1, (conn_handle, addr_type, addr)) # IRQ_CENTRAL_CONNECT = 1
