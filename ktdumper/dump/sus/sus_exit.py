import time

import usb.core

from dump.dumper import Dumper


class SusExit(Dumper):
    primary = bytes.fromhex("ff e1 e0 44 00 06 fd ef 00 da 01")
    query = bytes.fromhex("ff fd ef fd ee 6f 00 01 20 fe")

    def set_mode(self, mode):
        try:
            self.dev.ctrl_transfer(0x41, 0x60, mode, 0, None)
        except usb.core.USBTimeoutError as error:
            raise RuntimeError(f"SET_MODE {mode:02x}: control request timed out") from error
        try:
            self.dev.read(0x81, 16)
        except usb.core.USBTimeoutError as error:
            raise RuntimeError(f"SET_MODE {mode:02x}: acknowledgement on endpoint 81 timed out") from error

    def activate(self):
        self.dev.default_timeout = 5000
        self.dev.ctrl_transfer(0x41, 0x62, 0, 0, b"\x02\xc0")
        self.dev.read(0x81, 16)
        self.set_mode(0xc0)

    def send(self, frame):
        block = frame + bytes(0x800 - len(frame) - 1) + b"\xfe"
        if self.dev.write(3, block) != len(block):
            raise RuntimeError("Incomplete USB write")

    def receive(self, seconds, query_on_reconnect=False):
        deadline = time.monotonic() + seconds
        data = bytearray()
        while time.monotonic() < deadline:
            if self.dev is None:
                self.dev = usb.core.find(idVendor=self.target_vid, idProduct=self.target_pid)
                if self.dev is None:
                    time.sleep(0.1)
                    continue
                self.activate()
                if query_on_reconnect:
                    self.send(self.query)
            try:
                data.extend(self.dev.read(0x82, 0x800, timeout=500))
                if b"\xfe" in data:
                    break
            except usb.core.USBTimeoutError:
                pass
            except usb.core.USBError as error:
                if error.errno != 19:
                    raise
                self.dev = None
                data.clear()
        return bytes(data)

    def execute(self, dev, output):
        self.dev = dev
        self.activate()
        response = self.receive(2)
        if self.primary not in response:
            if self.dev is None:
                raise RuntimeError("Phone disconnected before its updater state was identified")
            self.send(self.query)
            response = self.receive(60, query_on_reconnect=True)
            if bytes.fromhex("6f 00 02 30 00") in response:
                print("The phone is already in the regular OS.")
                return
            if bytes.fromhex("6f 00 02 30 40") in response:
                print("Updater state 0 -> state 1...")
                self.send(bytes.fromhex("ff e0 e1 44 00 05 fd ef 00 ca 01 01 fe"))
                response = self.receive(2)
                if self.primary not in response:
                    if self.dev is not None:
                        print("No primary startup yet; cycling USB service mode...")
                        try:
                            self.set_mode(0)
                            time.sleep(1)
                            self.set_mode(0xc0)
                        except usb.core.USBError as error:
                            if error.errno != 19:
                                raise
                            self.dev = None
                    response = self.receive(60)
        if self.primary not in response:
            raise RuntimeError(f"Primary updater not confirmed: {response.hex(' ')}")
        self.send(bytes.fromhex("ff e0 e1 44 00 05 fd ef 00 ca 01 00 fe"))
        response = self.receive(20)
        if bytes.fromhex("ff fd ee fd ef 6f") not in response:
            raise RuntimeError(f"Unexpected exit response: {response.hex(' ')}")
        print("Exit response received; the phone should restart into the regular OS.")
