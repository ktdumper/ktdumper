import tqdm

from dump.serial_nec.serial_nec_protocol import SerialNecProtocol
from dump.serial_nec.serial_nec_exit_service_mode import exit_service_mode


class SerialNecMemoryDumper(SerialNecProtocol):

    def parse_opts(self, opts):
        super().parse_opts(opts)
        self.base = opts['base']
        self.size = opts['size']
        assert self.base % 128 == 0
        assert self.size % 128 == 0

    def execute(self, dev, output):
        self.connect(dev)
        with output.mksuff('.bin') as outf:
            with tqdm.tqdm(total=self.size, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for addr in range(self.base, self.base + self.size, 128):
                    data = self.read_flash(b'\xd1\x0c\x07' + self.nibbles(addr, 8), 128)
                    outf.write(data)
                    outf.flush()
                    bar.update(len(data))
        exit_service_mode(self.port)
        self.port.close()
