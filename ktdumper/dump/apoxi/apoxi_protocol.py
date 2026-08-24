import struct
import time
import usb.util

from dump.dumper import Dumper

# To use this protocol boot the phone with * + # + power key
# There should be 8 vertical stripes visible on the phone
# Then connect it to the PC with a cable with power switch OFF


NODE_SIE_COPYRIGHT_BANNER = """================================================================================
ApoxiProtocol is based off "node-sie-serial"
--------------------------------------------------------------------------------
https://github.com/siemens-mobile-hacks/node-sie-serial
MIT License
Copyright (c) 2024 Siemens Mobile Hackers
================================================================================"""

# auth, keys, etc from node-sie-serial
RAND1 = 5500
RAND2 = 5500
RAND3 = 5500
RAND4 = 0
KEY1 = bytes.fromhex("A3F9A49C5DE37D922511958D56CE51F2")
KEY2 = 0x17D2
KEY3 = bytes(16)
KEY4 = 0


def encapsulate(request):
    positions = []
    escaped = bytearray(request)
    for index, value in enumerate(escaped):
        if value == 0x0D:
            positions.append(index + 14)
            escaped[index] = 0x0C
    return b"AT#" + bytes([len(positions), *positions]) + escaped + b"\r"


class ApoxiProtocol(Dumper):

    def read_exactly(self, length):
        data = bytearray()
        while len(data) < length:
            data += bytes(self.dev.read(0x81, 0x1000, timeout=5000))
        assert len(data) == length
        return bytes(data)

    def command(self, request, response_opcode, response_length):
        request = encapsulate(request)
        assert self.dev.write(0x02, request, timeout=5000) == len(request)

        response = self.read_exactly(response_length)
        assert struct.unpack_from("<H", response)[0] == response_opcode
        assert len(response) == 4 + struct.unpack_from("<H", response, 2)[0]
        return response

    def authenticate(self):
        value = ((KEY2 ^ RAND1) + RAND2 + 0x4ED5) & 0xFFFF
        request = struct.pack("<HHHHH", 0x0058, RAND1, value, RAND2, RAND3)
        response = self.command(request, 0x0057, 10)

        key_rotate = (struct.unpack_from("<H", response, 6)[0] - RAND2) & 0xF
        assert struct.unpack_from("<H", response, 4)[0] == (
            (RAND1 * 8 - RAND2) ^ 0xD427
        ) & 0xFFFF
        assert struct.unpack_from("<H", response, 8)[0] == (
            (KEY1[key_rotate] << 4) ^ 0x7F39
        ) & 0xFFFF
        print(f"handshake 1 passed, key rotation {key_rotate}")

        value = (KEY1[0xF - key_rotate] ^ 0x4D33) & 0xFFFF
        self.command(struct.pack("<HHHH", 0x0059, 0, value, 0), 0x0056, 8)
        print("handshake 2 passed")

    def read(self, addr, sz):
        assert sz <= 0x80

        resp = self.command(struct.pack("<HHI", 0x0076, sz, addr), 0x0077, 234)
        return resp[4:4+sz]

    def execute(self, dev, output):
        self.dev = dev
        self.output = output

        print(NODE_SIE_COPYRIGHT_BANNER)

        for number in (0, 1):
            if self.dev.is_kernel_driver_active(number):
                self.dev.detach_kernel_driver(number)
            usb.util.claim_interface(self.dev, number)

        self.dev.ctrl_transfer(0x21, 0x22, 3, 0, None)
        self.dev.ctrl_transfer(0x21, 0x20, 0, 0, struct.pack("<IBBB", 112500, 0, 0, 8))

        self.authenticate()
