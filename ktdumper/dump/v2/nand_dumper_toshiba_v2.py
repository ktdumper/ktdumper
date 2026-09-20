import struct
import tqdm



RETRIES = 8


class NandDumperToshiba_v2:

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.nand_data = opts["nand_data"]
        self.nand_addr = opts["nand_addr"]
        self.nand_cmd = opts["nand_cmd"]
        size = opts["size"]
        assert size % 4096 == 0
        self.num_pages = size // 4096

    def read_page(self, page):
        self.usb_send(struct.pack("<BI", 0x55, page))
        return self.usb_receive()

    def execute(self, dev, output):
        super().execute(dev, output)

        with output.mkfile("nand.bin") as nand_bin:
            with output.mkfile("nand.oob") as nand_oob:
                with tqdm.tqdm(total=4096*self.num_pages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                    for page in range(self.num_pages):
                        for retries in range(RETRIES):
                            data = self.read_page(page)

                            if (data[0] & 0x41) == 0x40:
                                data = data[1:]
                                break
                            else:
                                print("read page 0x{:X} returned error 0x{:X}, retrying".format(page, data[0]))

                                if retries == RETRIES-1:
                                    print("failed to read page 0x{:X}...".format(page))
                                    data = data[1:]

                        assert len(data) == 4224

                        nand_bin.write(data[0:4096])
                        nand_oob.write(data[4096:])

                        bar.update(4096)
