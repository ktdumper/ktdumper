import struct

from dump.dumper import Dumper


SLOW_READ = 1


def mask_packet(pkt):
    out = [0xFF]
    ck = 0
    for b in pkt:
        if b in [0xFD, 0xFE, 0xFF]:
            out.append(0xFD)
            out.append(b ^ 0x10)
        else:
            out.append(b)
        ck += b
    ck = (-ck) & 0xFF
    if ck in [0xFD, 0xFE, 0xFF]:
        out.append(0xFD)
        out.append(ck ^ 0x10)
    else:
        out.append(ck)
    out.append(0xFE)

    return bytearray(out)


def make_packet(cmd, subcmd, variable_payload=None):
    if variable_payload is None:
        variable_payload = b""
    packet = struct.pack("<BBBHBBBB", 0xE9, 0xE3, 0x42, 6 + len(variable_payload), 0, 0, cmd, subcmd) + variable_payload
    return mask_packet(packet)


def unmask_resp(resp):
    assert resp[0] == 0xFF
    assert resp[-1] == 0xFE
    resp = resp[1:-1]
    out = []
    x = 0
    while x < len(resp):
        if resp[x] == 0xFD:
            out.append(resp[x+1] ^ 0x10)
            x += 2
        else:
            out.append(resp[x])
            x += 1
    return bytearray(out)


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

        if opts.get("quirks", 0) & SLOW_READ:
            self.chunk = 0x10
        else:
            self.chunk = 0x100

        self.patch = opts.get("patch", 0)

    def read_resp(self):
        resp = b""
        while True:
            resp += self.dev.read(0x87, 64)
            if resp.endswith(b"\xFE"):
                break
            elif b"\xFE" in resp:
                raise RuntimeError("mismatched packet masking")
        return unmask_resp(resp)

    def comm_oneway(self, cmd, subcmd=0, variable_payload=None):
        pkt = make_packet(cmd, subcmd, variable_payload)
        ret = self.dev.write(0x8, pkt)

    def comm(self, cmd, subcmd=0, variable_payload=None):
        self.comm_oneway(cmd, subcmd, variable_payload)
        return self.read_resp()

    def init_recovery(self):
        # go into serial comms mode => turns green led on for some, display on
        self.dev.ctrl_transfer(0x41, 0x60, 0x60, 2)
        self.dev.read(0x86, 64)

        if self.secret is not None:
            user_buffer = self.secret + checksum2(self.secret) + b"\x00" * 0x20
            self.comm_oneway(0x13, subcmd=2, variable_payload=user_buffer)
            self.comm(3, variable_payload=b"\x22")
        else:
            self.comm(3, variable_payload=b"\x00")

    def cmd_read(self, addr, sz):
        if self.patch:
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
