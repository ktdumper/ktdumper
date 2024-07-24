import tqdm
import struct

class CommonMemoryDumper:

    mem_chunk = 0x1000

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.base = opts["base"]
        self.size = opts["size"]

    def execute(self, dev, output):
        super().execute(dev, output)

        with output.mksuff(".bin") as outf:
            chunk = self.mem_chunk

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
