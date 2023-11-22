import tqdm
import usb.core
import struct

from util.payload_builder import PayloadBuilder


RETRIES = 8


class CommonOnenandFast:

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.page_size = 4096
        self.oob_size = 128
        self.pages_per_block = 64

        assert opts["size"] % self.page_size == 0
        self.num_pages = opts["size"] // self.page_size
        self.onenand_addr = opts["onenand_addr"]
        self.onenand_DATARAM = self.onenand_addr + 2*0x200
        self.onenand_SPARERAM = self.onenand_addr + 2*0x8010

        self.usb_command = opts["usb_command"]
        self.usb_data = opts["usb_data"]
        self.usb_datasz = opts["usb_datasz"]
        self.usb_respfunc = opts["usb_respfunc"]
        self.payload_base = opts["payload_base"]

    def unwrap_read(self, data, size):
        assert len(data) == size + 10
        return data[9:-1]

    def _onenand_read(self, page):
        data = b""

        # load the page to the onenand buffer and retrieve its first 256 bytes
        self.comm(3, variable_payload=struct.pack("<BBI", 1, 0, page))
        data += self.unwrap_read(self.read_resp(), 256)

        # retrieve the remainder of the page through the read memory command
        for off in range(256, self.page_size, 256):
            self.comm(3, variable_payload=struct.pack("<BBIH", 1, 1, self.onenand_DATARAM+off, 256))
            data += self.unwrap_read(self.read_resp(), 256)

        # retrieve the oob data
        self.comm(3, variable_payload=struct.pack("<BBIH", 1, 1, self.onenand_SPARERAM, self.oob_size))
        data += self.unwrap_read(self.read_resp(), self.oob_size)

        return data

    def onenand_read_page(self, page):
        # if it fails even once, re-validate the re-read attempt
        validation = False

        for x in range(RETRIES):
            try:
                first = self._onenand_read(page)
                if validation:
                    second = self._onenand_read(page)
                    third = self._onenand_read(page)
                    assert first == second
                    assert first == third
                return first
            except usb.core.USBTimeoutError:
                print("_onenand_read(page=0x{:X}) failed, retrying {} times".format(page, x+1))
                self.dev.reset()
                validation = True

        raise RuntimeError("unable to read page=0x{:X}".format(page))

    def execute(self, dev, output):
        super().execute(dev, output)

        payload = PayloadBuilder("onenand_fast.c").build(
            base=self.payload_base,
            usb_command=self.usb_command,
            usb_data=self.usb_data,
            usb_datasz=self.usb_datasz,
            usb_respfunc=self.usb_respfunc,
            onenand_addr=self.onenand_addr,
        )
        self.cmd_write(self.payload_base, payload)

        print("Dumping OneNAND & OOB")
        with output.mkfile("onenand.bin") as onenand_bin:
            with output.mkfile("onenand.oob") as onenand_oob:
                chunk = self.page_size + self.oob_size
                with tqdm.tqdm(total=chunk*self.num_pages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                    for page in range(self.num_pages):
                        full = self.onenand_read_page(page)

                        data = full[0:self.page_size]
                        spare = full[self.page_size:]
                        assert len(data) == self.page_size
                        assert len(spare) == self.oob_size

                        onenand_bin.write(data)
                        onenand_oob.write(spare)

                        bar.update(chunk)
