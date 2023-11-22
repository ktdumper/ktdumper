import tqdm
import struct

from dump.common_rw_access import CommonRwAccess
from util.payload_builder import PayloadBuilder

import usb.core


RETRIES = 8


class CommonOnenandDumper(CommonRwAccess):

    def parse_opts(self, opts):
        super().parse_opts(opts)

        if opts.get("has_4k_pages", False):
            self.page_size = 4096
            self.oob_size = 128
            self.inline_spare = True
        else:
            self.page_size = 2048
            self.oob_size = 64
            self.inline_spare = False

        self.pages_per_block = 64

        assert opts["size"] % self.page_size == 0
        self.num_pages = opts["size"] // self.page_size
        self.onenand_addr = opts["onenand_addr"]

        self.onenand_REG_START_ADDRESS1 = self.onenand_addr + 2*0xF100
        self.onenand_REG_START_ADDRESS2 = self.onenand_addr + 2*0xF101
        self.onenand_REG_START_ADDRESS8 = self.onenand_addr + 2*0xF107
        self.onenand_REG_START_BUFFER = self.onenand_addr + 2*0xF200
        self.onenand_REG_INTERRUPT = self.onenand_addr + 2*0xF241
        self.onenand_REG_COMMAND = self.onenand_addr + 2*0xF220
        self.onenand_DATARAM = self.onenand_addr + 2*0x200
        self.onenand_SPARERAM = self.onenand_addr + 2*0x8010

    def _onenand_read(self, page, cmd, read_ptr, read_sz):
        self.writeh(page // self.pages_per_block, self.onenand_REG_START_ADDRESS1)
        self.writeh(0, self.onenand_REG_START_ADDRESS2)
        self.writeh((page % self.pages_per_block) << 2, self.onenand_REG_START_ADDRESS8)

        self.writeh((1 << 3) << 8, self.onenand_REG_START_BUFFER)

        self.writeh(0, self.onenand_REG_INTERRUPT)
        self.writeh(cmd, self.onenand_REG_COMMAND)

        # NOTE: not listening for the interrupt/read to complete, assume usb is slow enough it's not needed

        if self.inline_spare:
            return self.read(self.onenand_DATARAM, self.page_size) + self.read(self.onenand_SPARERAM, self.oob_size)
        else:
            return self.read(read_ptr, read_sz)

    def _onenand_read_retry(self, page, cmd, read_ptr, read_sz):
        # if it fails even once, re-validate the re-read attempt
        validation = False

        for x in range(RETRIES):
            try:
                first = self._onenand_read(page, cmd, read_ptr, read_sz)
                if validation:
                    second = self._onenand_read(page, cmd, read_ptr, read_sz)
                    third = self._onenand_read(page, cmd, read_ptr, read_sz)
                    assert first == second
                    assert first == third
                return first
            except usb.core.USBTimeoutError:
                print("_onenand_read(page=0x{:X}) failed, retrying {} times".format(page, x+1))
                self.dev.reset()
                validation = True

        raise RuntimeError("unable to read page=0x{:X}".format(page))

    def onenand_read_page(self, page):
        return self._onenand_read_retry(page, 0x00, self.onenand_DATARAM, self.page_size)

    def onenand_read_oob(self, page):
        return self._onenand_read_retry(page, 0x13, self.onenand_SPARERAM, self.oob_size)

    def execute(self, dev, output):
        super().execute(dev, output)

        # devices with 4K pages will read OOB together with the data page
        if self.inline_spare:
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
        else:
            print("Dumping OneNAND")
            with output.mkfile("onenand.bin") as outf:
                with tqdm.tqdm(total=self.page_size*self.num_pages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                    for page in range(self.num_pages):
                        outf.write(self.onenand_read_page(page))
                        bar.update(self.page_size)

            print("Dumping OOB")
            with output.mkfile("onenand.oob") as outf:
                with tqdm.tqdm(total=self.oob_size*self.num_pages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                    for page in range(self.num_pages):
                        outf.write(self.onenand_read_oob(page))
                        bar.update(self.oob_size)
