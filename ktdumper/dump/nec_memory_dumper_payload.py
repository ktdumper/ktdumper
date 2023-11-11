import tqdm
import struct

from dump.nec_protocol import NecProtocol
from util.payload_builder import PayloadBuilder


class NecMemoryDumperPayload(NecProtocol):

    """ A version of NecMemoryDumper that goes through the code exec payload, for phones with delays """

    def __init__(self, name, base, size, payload_base=0x30000000, quirks=0):
        super().__init__(quirks)
        self.name = name
        self.base = base
        self.size = size
        self.payload_base = payload_base

    def execread(self, addr, sz):
        self.comm(3, variable_payload=struct.pack("<BIH", 1, addr, sz))
        data = self.read_resp()
        assert len(data) == sz + 10
        return data[9:-1]

    def execute(self, dev, output):
        super().execute(dev, output)

        print("!! Restart the phone before running another payload !!")

        payload = PayloadBuilder("memory_read.c").build(base=self.payload_base)
        self.cmd_write(self.payload_base, payload)

        with output.mkfile(self.name) as outf:
            chunk = 0x10
            end = self.base + self.size
            with tqdm.tqdm(total=self.size, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for addr in range(self.base, end, chunk):
                    remainder = end - addr
                    if remainder < chunk:
                        chunk = remainder
                    data = self.execread(addr, chunk)
                    outf.write(data)

                    bar.update(chunk)
