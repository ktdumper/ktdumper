import struct
import tqdm
import usb.core



RETRIES = 8


class NandDumperLp_v2:

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
        return self.usb_receive()

    def execute(self, dev, output):
        super().execute(dev, output)

        with output.mkfile("nand.bin") as nand_bin:
            with output.mkfile("nand.oob") as nand_oob:
                with tqdm.tqdm(total=2048*self.num_pages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                    for page in range(self.num_pages):
                        for retries in range(RETRIES):
                            data = self.read_page(page)

                            if data[0] in [0xE0, 0x60]:
                                data = data[1:]
                                break
                            else:
                                # silence first retry for error 0xC0 since it happens very often and is "normal"?
                                if data[0] != 0xC0 or retries > 0:
                                    print("read page 0x{:X} returned error 0x{:X}, retrying".format(page, data[0]))

                                if retries == RETRIES-1:
                                    print("failed to read page 0x{:X}...".format(page))
                                    data = b"\xFF" * 2112

                        assert len(data) == 2112

                        nand_bin.write(data[0:2048])
                        nand_oob.write(data[2048:])

                        bar.update(2048)
