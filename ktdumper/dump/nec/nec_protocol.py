import struct
import time
import usb.core

from dump.dumper import Dumper


SLOW_READ = 1


def checksum2(data):
    s = 0
    for x in range(0, len(data), 2):
        s += struct.unpack("<H", data[x:x+2])[0]
    return struct.pack("<H", (-s) & 0xFFFF)


class NecProtocol(Dumper):

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.secret = opts.get("secret")
        if self.secret is not None:
            self.secret = bytes.fromhex(self.secret)

        self.panasonic_unlock = opts.get("panasonic_unlock")

        if opts.get("quirks", 0) & SLOW_READ:
            self.chunk = 0x10
        else:
            self.chunk = 0x100

        if opts.get("legacy_masking", False):
            self.MASKED_START = 0xC0
            self.MASKED_END = 0xC1
            self.MASKED_CHARS = [0x7D, 0xC0, 0xC1]
            self.MASKING_CHAR = 0x7D
            self.MASK_XOR = 0x20
        else:
            self.MASKED_START = 0xFF
            self.MASKED_END = 0xFE
            self.MASKED_CHARS = [0xFD, 0xFE, 0xFF]
            self.MASKING_CHAR = 0xFD
            self.MASK_XOR = 0x10

    # TODO: this should really be split into mask and checksum as separate things
    def mask_packet(self, pkt):
        out = [self.MASKED_START]
        ck = 0
        for b in pkt:
            if b in self.MASKED_CHARS:
                out.append(self.MASKING_CHAR)
                out.append(b ^ self.MASK_XOR)
            else:
                out.append(b)
            ck += b
        ck = (-ck) & 0xFF
        if ck in self.MASKED_CHARS:
            out.append(self.MASKING_CHAR)
            out.append(ck ^ self.MASK_XOR)
        else:
            out.append(ck)
        out.append(self.MASKED_END)

        return bytearray(out)

    def make_packet(self, cmd, subcmd, variable_payload=None):
        if variable_payload is None:
            variable_payload = b""
        packet = struct.pack("<BBBHBBBB", 0xE9, 0xE3, 0x42, 6 + len(variable_payload), 0, 0, cmd, subcmd) + variable_payload
        return self.mask_packet(packet)

    def unmask_resp(self, resp):
        assert resp[0] == self.MASKED_START
        assert resp[-1] == self.MASKED_END
        resp = resp[1:-1]
        out = []
        x = 0
        while x < len(resp):
            if resp[x] == self.MASKING_CHAR:
                out.append(resp[x+1] ^ self.MASK_XOR)
                x += 2
            else:
                out.append(resp[x])
                x += 1
        return bytearray(out)

    def read_resp(self):
        resp = b""
        tgt = bytes([self.MASKED_END])
        while True:
            resp += self.dev.read(0x87, 64)
            if resp.endswith(tgt):
                break
            elif tgt in resp:
                raise RuntimeError("mismatched packet masking, resp={}".format(resp.hex()))
        return self.unmask_resp(resp)

    def comm_oneway(self, cmd, subcmd=0, variable_payload=None):
        pkt = self.make_packet(cmd, subcmd, variable_payload)
        ret = self.dev.write(0x8, pkt)

    def comm(self, cmd, subcmd=0, variable_payload=None):
        self.comm_oneway(cmd, subcmd, variable_payload)
        return self.read_resp()

    def do_panasonic_unlock(self):
        if self.panasonic_unlock == "p906i":
            ptr_to_zero = 0x8024dbeb
            payload_pre_sz = 0x8022c840
            payload_pre = 0x80235660
            g_ep = 0x8024db47
            auth_flags = 0x8022c244
            restore_setup_buf = 0x8024db97
        elif self.panasonic_unlock == "p705i":
            ptr_to_zero = 0x8024dc0b
            payload_pre_sz = 0x8022c860
            payload_pre = 0x80235680
            g_ep = 0x8024db67
            auth_flags = 0x8022c264
            restore_setup_buf = 0x8024dbb7
        else:
            raise RuntimeError("unsupported value for panasonic_unlock: {}".formnat(self.panasonic_unlock))

        # preload reasonable data into setup buffer
        self.dev.ctrl_transfer(0x80, 0x06, 0x200, 0x00, 0x100)

        # overwrite pointer to setup packet contents so next ctrl_transfer's wValue/wIndex writes into the payload_pre_sz
        payload = b"\xFF" + b"\x00" * (g_ep - payload_pre) + struct.pack("<II", ptr_to_zero, payload_pre_sz - 2)
        assert b"\xFE" not in payload
        assert b"\xFF" not in payload[1:]

        assert self.dev.write(8, payload) == len(payload)

        def write_at(addr, data):
            offset = (addr - payload_pre) & 0xFFFFFFFF
            self.dev.ctrl_transfer(0x80, 0x06, offset & 0xFFFF, offset >> 16, 0x100)
            self.dev.write(8, data)

        # set auth_passed=1, auth_required=0
        write_at(auth_flags, b"\x01\x00")

        # reset buffer size back to 0 and write a dummy no-op packet
        write_at(payload_pre, b"")
        noop = self.make_packet(0x02, 0)
        self.dev.write(8, noop[1:])

        # do the INIT cmd
        self.comm(3, variable_payload=b"\x00")

        # restore overwritten setup endpoint structure
        self.cmd_write(g_ep+4, struct.pack("<I", restore_setup_buf))

        # check we restored properly
        assert bytearray(self.dev.ctrl_transfer(0x80, 0x06, 0x303, 0x00, 0x100)) == bytes.fromhex("2003300030003000300030003000300030003000300030003000300030003000")

    def init_recovery(self):
        # go into serial comms mode => turns green led on for some, display on
        self.dev.ctrl_transfer(0x41, 0x60, 0x60, 2)
        self.dev.read(0x86, 64)
        time.sleep(3)
        self.dev = usb.core.find(idVendor=self.dev.idVendor, idProduct=self.dev.idProduct)

        if self.panasonic_unlock is not None:
            self.do_panasonic_unlock()
        elif self.secret is not None:
            user_buffer = self.secret + checksum2(self.secret) + b"\x00" * 0x20
            self.comm_oneway(0x13, subcmd=2, variable_payload=user_buffer)
            self.comm(3, variable_payload=b"\x22")
        else:
            self.comm(3, variable_payload=b"\x00")

    def cmd_read(self, addr, sz):
        if self.secret is not None:
            raise RuntimeError("this device does not support cmd_read")

        data = self.comm(6, 0, variable_payload=struct.pack("<IH", addr, sz))
        assert len(data) == sz + 10
        return data[9:-1]

    def cmd_write(self, addr, data):
        self.comm_oneway(4, variable_payload=struct.pack("<IH", addr, len(data)) + data)

    def cmd_exec(self):
        self.comm(3, variable_payload=b"\x01")

    def read(self, addr, sz):
        data = b""
        chunk = self.chunk
        end = addr + sz
        for addr in range(addr, end, chunk):
            if chunk > end - addr:
                chunk = end - addr
            data += self.cmd_read(addr, chunk)
        return data

    def write(self, addr, data):
        if len(data) % 2 == 1:
            data += b"\x00"
        self.cmd_write(addr, data)

    def execute(self, dev, output):
        self.dev = dev
        self.output = output

        self.init_recovery()
