import tqdm
import struct

from dump.nec_direct_usb import NecDirectUsb


class NecMemoryDumperPayload(NecDirectUsb):

    """ A version of NecMemoryDumper that goes through the code exec payload, for phones with delays """

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.base = opts["base"]
        self.size = opts["size"]

    def execread(self, addr, sz):
        self.comm(3, variable_payload=struct.pack("<BIH", 1, addr, sz))
        data = self.read_resp()
        assert len(data) == sz + 10
        return data[9:-1]

    def execute(self, dev, output):
        super().execute(dev, output)

        print("!! Restart the phone before running another payload !!")
        self.insert_payload("memory_read.c")

        with output.mksuff(".bin") as outf:
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
