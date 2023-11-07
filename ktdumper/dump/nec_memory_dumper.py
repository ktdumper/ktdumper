import tqdm

from dump.nec_protocol import NecProtocol


class NecMemoryDumper(NecProtocol):

    def __init__(self, name, base, size, quirks=0):
        super().__init__(quirks)
        self.name = name
        self.base = base
        self.size = size

    def execute(self, dev, output):
        super().execute(dev, output)

        with output.mkfile(self.name) as outf:
            chunk = 0x1000
            end = self.base + self.size
            with tqdm.tqdm(total=self.size, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for addr in range(self.base, end, chunk):
                    remainder = end - addr
                    if remainder < chunk:
                        chunk = remainder
                    data = self.read(addr, chunk)
                    outf.write(data)

                    bar.update(chunk)
