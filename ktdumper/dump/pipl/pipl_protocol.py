import struct

from dump.dumper import Dumper


def mask_packet(pkt):
    out = [0xFF]
    ck = 0
    for b in pkt:
        out.append(b)
        ck += b
    ck = (-ck) & 0xFF
    out.append(ck)
    out.append(0xFE)

    return bytearray(out)


def make_packet(cmd, subcmd, variable_payload=None):
    if variable_payload is None:
        variable_payload = b""
    packet = struct.pack("<BBBHBBBB", 0xE9, 0xE3, 0x42, 5 + len(variable_payload), 0, 0, cmd, subcmd) + variable_payload
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


class PiplProtocol(Dumper):

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.chunk = 0x100
        self.secret = None

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
        # go into serial comms mode => turns green led on
        self.dev.ctrl_transfer(0x40, 0x60, 0x60, 0)

    def execute(self, dev, output):
        self.dev = dev
        self.output = output

        self.init_recovery()

    def cmd_read(self, addr, sz):
        data = self.comm(6, 0, variable_payload=struct.pack("<IH", addr, sz))
        assert len(data) == sz + 10
        return data[9:-1]

    def read(self, addr, sz):
        data = b""
        chunk = self.chunk
        end = addr + sz
        for addr in range(addr, end, chunk):
            if chunk > end - addr:
                chunk = end - addr
            data += self.cmd_read(addr, chunk)
        return data

    def cmd_write(self, addr, data):
        self.comm_oneway(4, variable_payload=struct.pack("<IH", addr, len(data)) + data)

    def cmd_exec(self):
        self.comm(3, variable_payload=b"\x01")

    def write(self, addr, data):
        if len(data) % 2 == 1:
            data += b"\x00"
        self.cmd_write(addr, data)
