import struct


class RwAccess_v2:

    def readb(self, addr):
        self.usb_send(struct.pack("<BI", 0x10, addr))
        return struct.unpack("B", self.usb_receive())[0]

    def readh(self, addr):
        self.usb_send(struct.pack("<BI", 0x11, addr))
        return struct.unpack("<H", self.usb_receive())[0]

    def readw(self, addr):
        self.usb_send(struct.pack("<BI", 0x12, addr))
        return struct.unpack("<I", self.usb_receive())[0]

    def writeb(self, val, addr):
        self.usb_send(struct.pack("<BIB", 0x20, addr, val))

    def writeh(self, val, addr):
        self.usb_send(struct.pack("<BIH", 0x21, addr, val))

    def writew(self, val, addr):
        self.usb_send(struct.pack("<BII", 0x22, addr, val))

    def read64(self, addr):
        self.usb_send(struct.pack("<BI", 0x60, addr))
        return self.usb_receive()

    def read(self, addr, size):
        assert size % 64 == 0

        data = b""
        while size > 0:
            data += self.read64(addr)
            addr += 64
            size -= 64
        return data

    def execute(self, dev, output):
        super().execute(dev, output)

        # validate payload set up correctly
        self.writew(0xDEADBEEF, self.payload_base+0x10000)
        assert self.readw(self.payload_base+0x10000) == 0xDEADBEEF
        self.writeh(0xEE, self.payload_base+0x10000)
        assert self.readw(self.payload_base+0x10000) == 0xDEAD00EE
