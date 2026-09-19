import tqdm

from dump.serial_fujitsu.serial_fujitsu_protocol import SerialFujitsuProtocol


class SerialFujitsuMemoryDumper(SerialFujitsuProtocol):

    def parse_opts(self, opts):
        super().parse_opts(opts)
        self.base = opts['base']
        self.size = opts['size']
        assert self.base % 4096 == 0
        assert self.size > 0 and self.size % 4096 == 0

    def execute(self, dev, output):
        self.connect(dev)
        with output.mksuff('.bin') as outf:
            with tqdm.tqdm(total=self.size, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for addr in range(self.base, self.base + self.size, 4096):
                    data = self.read_flash(addr, 4096)
                    outf.write(data)
                    outf.flush()
                    bar.update(len(data))
        self.disconnect()
