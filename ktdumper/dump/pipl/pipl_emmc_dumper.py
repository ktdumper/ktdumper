import struct
import usb.core
import tqdm

from dump.pipl.pipl_exploit import PiplExploit
from util.payload_builder import PayloadBuilder


PAGE_SIZE = 512
PAGES_PER_CMD = 32
PAGES_x = PAGE_SIZE * PAGES_PER_CMD
RETRIES = 5


class PiplEmmcDumper(PiplExploit):

    def parse_opts(self, opts):
        super().parse_opts(opts)

        assert opts["size"] % PAGES_x == 0
        self.num_pages = opts["size"] // PAGES_x

        self.emmc_read_and_dcache = opts["emmc_read_and_dcache"]
        self.usb_command = opts["usb_command"]
        self.usb_data = opts["usb_data"]
        self.usb_datasz = opts["usb_datasz"]
        self.usb_respfunc = opts["usb_respfunc"]
        self.payload_base = opts["payload_base"]

    def unwrap_read(self, data, size):
        assert len(data) == size + 10
        return data[9:-1]

    def _emmc_read_page(self, page):
        self.comm(3, variable_payload=struct.pack("<BI", 1, page))
        return self.unwrap_read(self.read_resp(), PAGES_x)

    def emmc_read_page(self, page):
        # if it fails even once, re-validate the re-read attempt
        validation = False

        for x in range(RETRIES):
            try:
                first = self._emmc_read_page(page)
                if validation:
                    second = self._emmc_read_page(page)
                    third = self._emmc_read_page(page)
                    assert first == second
                    assert first == third
                return first
            except usb.core.USBTimeoutError:
                print("_emmc_read_page(page=0x{:X}) failed, retrying {} times".format(page, x+1))
                self.dev.reset()
                self.dev = usb.core.find(idVendor=self.dev.idVendor, idProduct=self.dev.idProduct)
                validation = True

        raise RuntimeError("unable to read page=0x{:X}".format(page))

    def execute(self, dev, output):
        super().execute(dev, output)

        payload = PayloadBuilder("emmc_dump.c").build(
            base=self.payload_base,
            emmc_read_and_dcache=self.emmc_read_and_dcache,
            usb_command=self.usb_command,
            usb_data=self.usb_data,
            usb_datasz=self.usb_datasz,
            usb_respfunc=self.usb_respfunc,
        )
        self.cmd_write(self.payload_base, payload)

        print("Dumping eMMC")
        with output.mkfile("emmc.bin") as emmc_bin:
            with tqdm.tqdm(total=PAGES_x*self.num_pages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                for page in range(self.num_pages):
                    emmc_bin.write(self.emmc_read_page(page))
                    bar.update(PAGES_x)
