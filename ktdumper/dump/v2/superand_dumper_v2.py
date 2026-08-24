import struct
import tqdm



RETRIES = 8


class SuperandDumper_v2:

    def parse_opts(self, opts):
        super().parse_opts(opts)

        size = opts["size"]
        assert size % 2048 == 0
        self.num_pages = size // 2048

    def read_page(self, page):
        self.usb_send(struct.pack("<BI", 0x53, page))
        return self.usb_receive()

    def execute(self, dev, output):
        super().execute(dev, output)

        with output.mkfile("superand.bin") as superand_bin:
            with tqdm.tqdm(total=2048*self.num_pages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for page in range(self.num_pages):
                    for retries in range(RETRIES):
                        data = self.read_page(page)

                        if data[0] in [0xE0, 0x60, 0xC0]:
                            data = data[1:]
                            break
                        else:
                            if data[0] != 0xC0 or retries > 0:
                                print("read page 0x{:X} returned error 0x{:X}, retrying".format(page, data[0]))

                            if retries == RETRIES-1:
                                print("failed to read page 0x{:X}...".format(page))
                                data = b"\xFF" * 2048

                    assert len(data) == 2048

                    superand_bin.write(data)

                    bar.update(2048)
