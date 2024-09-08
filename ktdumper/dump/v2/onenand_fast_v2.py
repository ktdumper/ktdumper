from dump.common.common_onenand_dumper import CommonOnenandDumper

import struct
import tqdm


class OnenandFast_v2(CommonOnenandDumper):

    def read_page_and_oob(self, ddp, block, page):
        if self.page_size == 2048:
            onenand_cmd = 0x72
        elif self.page_size == 4096:
            onenand_cmd = 0x70
        else:
            raise RuntimeError("read_page_and_oob: misconfig, unsupported page size {}".format(self.page_size))

        try:
            self.usb_send(struct.pack("<BIIB", onenand_cmd, block, page, ddp))
            data = self.usb_receive()
        except Exception:
            print("exception reading block=0x{:X} page=0x{:X}".format(block, page))
            raise

        assert len(data) == self.page_size + self.oob_size
        return data
