import struct
import tqdm


class CommonShNandDumper:

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.nand_data = opts["nand_data"]
        self.nand_addr = opts["nand_addr"]
        self.nand_cmd = opts["nand_cmd"]
        size = opts["size"]
        assert size % 2048 == 0
        self.num_pages = size // 2048

    def read_fully(self, sz):
        data = b""
        while len(data) < sz:
            data += self.dev.read(0x82, 512)
        assert len(data) == sz
        return data

    def execute(self, dev, output):
        super().execute(dev, output)

        with output.mkfile("nand.bin") as nand_bin:
            with output.mkfile("nand.oob") as nand_oob:
                with tqdm.tqdm(total=2048*self.num_pages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                    for page in range(self.num_pages):
                        self.dev.write(3, struct.pack("<BI", 0x52, page))
                        data = self.read_fully(1)
                        for x in range(33):
                            self.dev.write(3, b"\x00")
                            data += self.read_fully(64)

                        if data[0] == 0xE0:
                            data = data[1:]
                        else:
                            print("read page 0x{:X} returned error 0x{:X}".format(x, page[0]))
                            data = b"\xFF" * 2112

                        assert len(data) == 2112

                        nand_bin.write(data[0:2048])
                        nand_oob.write(data[2048:])

                        bar.update(2048)
