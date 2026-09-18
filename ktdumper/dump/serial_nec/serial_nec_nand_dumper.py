import tqdm

from dump.serial_nec.serial_nec_protocol import SerialNecProtocol
from dump.serial_nec.serial_nec_exit_service_mode import exit_service_mode


class SerialNecNandDumper(SerialNecProtocol):

    def parse_opts(self, opts):
        super().parse_opts(opts)
        assert opts['size'] % 512 == 0
        self.num_pages = opts['size'] // 512

    def nand_read_page_and_oob(self, page):
        address = self.nibbles(page // 32, 3) + self.nibbles(page % 32, 2)
        return (self.read_flash(b'\xd1\x0d\x05\x03\x01' + address + b'\x00', 256)
                + self.read_flash(b'\xd1\x0d\x05\x03\x01' + address + b'\x01', 256)
                + self.read_flash(b'\xd1\x0d\x05\x03\x02' + address, 16))

    def execute(self, dev, output):
        self.connect(dev)
        print('Dumping NAND & OOB')
        with output.mkfile('nand.bin') as nand, output.mkfile('nand.oob') as oob:
            with tqdm.tqdm(total=528*self.num_pages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for page in range(self.num_pages):
                    data = self.nand_read_page_and_oob(page)
                    nand.write(data[:512])
                    oob.write(data[512:])
                    oob.flush()
                    nand.flush()
                    bar.update(len(data))
        exit_service_mode(self.port)
        self.port.close()
