import tqdm

from dump.serial_mitsubishi.serial_mitsubishi_protocol import SerialMitsubishiProtocol


class SerialMitsubishiMemoryDumper(SerialMitsubishiProtocol):

    def parse_opts(self, opts):
        super().parse_opts(opts)
        self.base = opts['base']
        self.size = opts['size']
        assert self.size > 0 and self.size % 2 == 0

    def execute(self, dev, output):
        self.connect(dev)
        with output.mksuff('.bin') as outf:
            with tqdm.tqdm(total=self.size, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for offset in range(0, self.size, 254):
                    size = min(254, self.size - offset)
                    data = self.read_flash(self.base + offset, size)
                    outf.write(data)
                    outf.flush()
                    bar.update(len(data))
