import struct

from util.payload_builder import PayloadBuilder


class CommonRwAccess:

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.payload_base = opts["payload_base"]
        self.payload_COMMAND = self.payload_base+0x400
        self.payload_OUTPUT = self.payload_base+0x800

    def rw_addr(self, is_wr, size, addr, val=0):
        cmd = struct.pack("<BBII", is_wr, size, addr, val)
        self.write(self.payload_COMMAND, cmd)
        self.cmd_exec()
        ret = 0
        if is_wr == 0:
            data = self.read(self.payload_OUTPUT, 4)
            if size == 1:
                ret = data[0]
            elif size == 2:
                ret = struct.unpack_from("<H", data)[0]
            elif size == 4:
                ret = struct.unpack_from("<I", data)[0]
        return ret

    def readb(self, addr):
        return self.rw_addr(0, 1, addr)

    def readh(self, addr):
        return self.rw_addr(0, 2, addr)

    def readw(self, addr):
        return self.rw_addr(0, 4, addr)

    def writeb(self, val, addr):
        return self.rw_addr(1, 1, addr, val)

    def writeh(self, val, addr):
        return self.rw_addr(1, 2, addr, val)

    def writew(self, val, addr):
        return self.rw_addr(1, 4, addr, val)

    def execute(self, dev, output):
        super().execute(dev, output)

        payload = PayloadBuilder("peek_poke.c").build(base=self.payload_base)
        self.cmd_write(self.payload_base, payload)

        # validate payload set up correctly
        self.writew(0xDEADBEEF, self.payload_base+0x600)
        assert self.readw(self.payload_base+0x600) == 0xDEADBEEF
        self.writeh(0xEE, self.payload_base+0x600)
        assert self.readw(self.payload_base+0x600) == 0xDEAD00EE

        print("!! Restart the phone before running another payload !!")
