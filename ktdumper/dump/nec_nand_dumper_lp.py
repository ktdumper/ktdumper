import tqdm
import struct
import time

from dump.nec_direct_usb import NecDirectUsb


class NecNandDumperLp(NecDirectUsb):

    def parse_opts(self, opts):
        super().parse_opts(opts)

        assert opts["size"] % 2048 == 0
        self.num_pages = opts["size"] // 2048

        self.nand_data = opts["nand_data"]
        self.nand_cmd = opts["nand_cmd"]
        self.nand_addr = opts["nand_addr"]

    def nand_read_page_and_oob(self, page):
        # perform nand page readout
        self.comm(3, variable_payload=struct.pack("<BBI", 1, 0, page))

        nand = b""

        # transmit the data back to us
        chunk = 0x10
        for addr in range(self.payload_base+0x1000, self.payload_base+0x1000+0x840, chunk):
            self.comm(3, variable_payload=struct.pack("<BBIH", 1, 1, addr, chunk))
            data = self.read_resp()
            assert len(data) == chunk + 10
            nand += data[9:-1]

        return nand[0:0x840]

    def execute(self, dev, output):
        super().execute(dev, output)

        self.insert_payload("dump_nand_lp_and_send.c",
            nand_data=self.nand_data,
            nand_cmd=self.nand_cmd,
            nand_addr=self.nand_addr)

        print("Dumping NAND & OOB")
        with output.mkfile("nand.bin") as nand_bin:
            with output.mkfile("nand.oob") as nand_oob:
                with tqdm.tqdm(total=2112*self.num_pages, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                    for page in range(self.num_pages):
                        data = self.nand_read_page_and_oob(page)

                        assert len(data) == 0x840
                        nand_bin.write(data[0:0x800])
                        nand_oob.write(data[0x800:0x840])

                        bar.update(2112)
