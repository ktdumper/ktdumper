import struct
import tqdm
import usb.core

from dump.sh_g1.sh_g1_protocol import ShG1Protocol



RETRIES = 8


class ShG1NandDumper(ShG1Protocol):

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.nand_data = opts["nand_data"]
        self.nand_addr = opts["nand_addr"]
        self.nand_cmd = opts["nand_cmd"]
        size = opts["size"]
        assert size % 2048 == 0
        self.num_pages = size // 2048

    def read_page(self, page):
        self.usb_send(struct.pack("<BI", 0x52, page))
        data = self.usb_receive()
        assert len(data) == 0x841
        return data

    def execute(self, dev, output):
        super().execute(dev, output)

        with output.mkfile("nand_mixed.bin") as nand_bin:
            with tqdm.tqdm(total=2048*self.num_pages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for page in range(self.num_pages):
                    for retries in range(RETRIES):
                        data = self.read_page(page)

                        if data[-1] in [0xE0, 0x60]:
                            data = data[:-1]
                            break
                        else:
                            # silence first retry for error 0xC0 since it happens very often and is "normal"?
                            if data[-1] != 0xC0 or retries > 0:
                                print("read page 0x{:X} returned error 0x{:X}, retrying".format(page, data[-1]))

                            if retries == RETRIES-1:
                                print("failed to read page 0x{:X}...".format(page))
                                data = b"\xFF" * 2112

                    assert len(data) == 2112

                    nand_bin.write(data)

                    bar.update(2048)
