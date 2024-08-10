import struct

from util.payload_builder import PayloadBuilder


class NecPiplRwAccess:

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.payload_base = opts["payload_base"]
        self.payload_COMMAND = self.payload_base+0x400
        self.payload_OUTPUT = self.payload_base+0x800

        self.usb_command = opts.get("usb_command")
        self.usb_data = opts.get("usb_data")
        self.usb_datasz = opts.get("usb_datasz")
        self.usb_respfunc = opts.get("usb_respfunc")
        self.payload_base = opts.get("payload_base")

    def rw_addr(self, is_wr, size, addr, val=0):
        cmd = struct.pack("<BBII", is_wr, size, addr, val)
        self.write(self.payload_COMMAND, cmd)
        self.cmd_exec()
        ret = 0
        if is_wr == 0:
            if self.secret:
                data = self.read_resp()
                assert len(data) == 14
                data = data[9:-1]
            else:
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

    def read64(self, addr):
        assert self.secret is not None

        cmd = struct.pack("<BBI", 2, 0, addr)
        self.write(self.payload_COMMAND, cmd)
        self.cmd_exec()
        data = self.read_resp()
        assert len(data) == 10 + 64
        data = data[9:-1]
        return data

    def read(self, addr, sz):
        if not self.secret:
            return super().read(addr, sz)

        data = b""
        for x in range(0, sz, 64):
            chunk = min(64, sz - x)
            data += self.read64(addr + x)[0:chunk]
        return data

    def execute(self, dev, output):
        super().execute(dev, output)

        kwargs = {
            "base": self.payload_base
        }

        # later NEC phones don't have the read memory command anymore so instead we make our payload send data out
        if self.secret:
            kwargs.update(dict(
                usb_command=self.usb_command,
                usb_data=self.usb_data,
                usb_datasz=self.usb_datasz,
                usb_respfunc=self.usb_respfunc,
                patch=self.patch,
            ))

        payload = PayloadBuilder("peek_poke.c").build(**kwargs)
        self.cmd_write(self.payload_base, payload)

        # must execute one no-op first to trigger the smc cleanup code
        if self.secret:
            self.cmd_exec()

        # validate payload set up correctly
        self.writew(0xDEADBEEF, self.payload_base+0x600)
        assert self.readw(self.payload_base+0x600) == 0xDEADBEEF
        self.writeh(0xEE, self.payload_base+0x600)
        assert self.readw(self.payload_base+0x600) == 0xDEAD00EE

        print("!! Restart the phone before running another payload !!")
