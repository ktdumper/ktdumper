import tqdm
import struct

CHUNK = 64

class CommonShMemoryDumper:

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.base = opts["base"]
        self.size = opts["size"]

    def read(self, addr, chunk):
        assert chunk == CHUNK
        self.dev.write(3, struct.pack("<BI", 0x60, addr))
        data = b""
        while len(data) != CHUNK:
            data += self.dev.read(0x82, 512)
        assert len(data) == CHUNK
        return data

    def execute(self, dev, output):
        super().execute(dev, output)

        with output.mksuff(".bin") as outf:
            chunk = CHUNK

            assert self.base % chunk == 0
            assert self.size % chunk == 0

            end = self.base + self.size
            with tqdm.tqdm(total=self.size, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for addr in range(self.base, end, chunk):
                    remainder = end - addr
                    if remainder < chunk:
                        chunk = remainder
                    data = self.read(addr, chunk)
                    outf.write(data)

                    bar.update(chunk)
