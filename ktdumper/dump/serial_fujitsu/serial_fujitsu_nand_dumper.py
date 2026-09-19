import re
import time

import tqdm

from dump.serial_fujitsu.serial_fujitsu_protocol import SerialFujitsuProtocol


class SerialFujitsuNandDumper(SerialFujitsuProtocol):

    def parse_opts(self, opts):
        super().parse_opts(opts)
        assert opts['size'] > 0 and opts['size'] % 512 == 0
        self.num_pages = opts['size'] // 512
        assert self.num_pages <= 65536
        self.nand_data = opts['nand_data']
        self.nand_cmd = opts['nand_cmd']
        self.nand_addr = opts['nand_addr']
        self.nand_gate = opts['nand_gate']

    def nand_command(self, value, resume=False):
        assert value in (0, 0x70, 0xff)
        assert not resume or value == 0
        width = 'MW' if resume else 'M'
        self.command(f'{width} {self.nand_cmd:08X} {value:X}')

    def nand_read_words(self, size):
        reply = self.command(f'DW {self.nand_data:08X} {size:X}')
        data = bytearray()
        for line in reply.replace(b'\r', b'').split(b'\n'):
            match = re.fullmatch(rb'([0-9A-Fa-f]{8})\s*:\s*((?:[0-9A-Fa-f]{4} ?)+)', line)
            if match:
                if int(match[1], 16) != self.nand_data + len(data):
                    raise ValueError('Unexpected NAND read address')
                for word in match[2].split():
                    data += int(word, 16).to_bytes(2, 'little')
        if len(data) != size:
            raise ValueError(f'Received {len(data)}/{size} NAND bytes')
        return bytes(data)

    def nand_read_page_and_oob(self, page):
        assert 0 <= page < self.num_pages
        self.nand_command(0)
        for value in (0, page & 255, page >> 8):
            self.command(f'M {self.nand_addr:08X} {value:X}')
        self.nand_command(0x70)
        for _ in range(10):
            if int.from_bytes(self.nand_read_words(2), 'little') & 0x40:
                break
            time.sleep(0.01)
        else:
            raise TimeoutError('NAND did not become ready')
        self.nand_command(0, resume=True)
        return self.nand_read_words(528)

    def execute(self, dev, output):
        self.connect(dev)
        self.command(f'MD {self.nand_gate:08X} 11')
        self.nand_command(0xff)
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
        self.nand_command(0xff)
        self.disconnect()
