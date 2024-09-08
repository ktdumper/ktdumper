import tqdm
import struct
import usb.core
import time

from dump.common.common_onenand_id import CommonOnenandIdMixin, deviceid_ddp, deviceid_density, deviceid_separation


SEPARATION_SLC = 0
SEPARATION_FLEX = 2

raw_sizes = {
    0: 16 * 1024 * 1024,
    1: 32 * 1024 * 1024,
    2: 64 * 1024 * 1024,
    3: 128 * 1024 * 1024,
    4: 256 * 1024 * 1024,
    5: 512 * 1024 * 1024,
    6: 1 * 1024 * 1024 * 1024,
    7: 2 * 1024 * 1024 * 1024,
}

SLC_PAGES_PER_BLOCK = 64
MLC_PAGES_PER_BLOCK = 128


class CommonOnenandDumper(CommonOnenandIdMixin):

    def _with_ddp(self, x, ddp):
        if ddp:
            return (1 << 15) | x
        return x

    def _onenand_cmd(self, ddp, block, page, cmd):
        self.writeh(self._with_ddp(block, ddp), self.onenand_REG_START_ADDRESS1)
        self.writeh(self._with_ddp(0, ddp), self.onenand_REG_START_ADDRESS2)
        self.writeh(page << 2, self.onenand_REG_START_ADDRESS8)

        self.writeh((1 << 3) << 8, self.onenand_REG_START_BUFFER)

        self.writeh(0, self.onenand_REG_INTERRUPT)
        self.writeh(cmd, self.onenand_REG_COMMAND)

        # wait for the read to complete
        while True:
            intr = self.readh(self.onenand_REG_INTERRUPT)
            if intr & 0x8000:
                break

        if intr & 0x80 != 0x80:
            raise RuntimeError("_onenand_cmd(ddp={}, block={}, page={}, cmd=0x{:X}) failed with intr=0x{:X}".format(
                ddp, block, page, cmd, intr))

    def _read_2k_page_and_oob(self, ddp, block, page):
        data = b""

        # READ
        self._onenand_cmd(ddp, block, page, 0x00)
        data += self.read(self.onenand_addr + 0x400, 2048)
        # READ SPARE
        self._onenand_cmd(ddp, block, page, 0x13)
        data += self.read(self.onenand_addr + 0x10020, 64)

        return data

    def _read_4k_page_and_oob(self, ddp, block, page):
        data = b""

        # READ
        self._onenand_cmd(ddp, block, page, 0x00)
        data += self.read(self.onenand_addr + 0x400, 4096)
        data += self.read(self.onenand_addr + 0x10020, 128)

        return data

    def read_page_and_oob(self, ddp, block, page):
        if self.page_size == 2048:
            return self._read_2k_page_and_oob(ddp, block, page)
        elif self.page_size == 4096:
            return self._read_4k_page_and_oob(ddp, block, page)
        else:
            raise RuntimeError("read_page_and_oob: misconfig, unsupported page size {}".format(self.page_size))

    def _dump_blocks_pages(self, prefixname, num_blocks, blocks_offset, num_pages_per_block):
        with self.output.mkfile(prefixname + ".bin") as onenand_bin:
            with self.output.mkfile(prefixname + ".oob") as onenand_oob:
                chunk = self.page_size + self.oob_size
                with tqdm.tqdm(total=chunk*num_pages_per_block*num_blocks*self.num_ddp, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                    for ddp in range(self.num_ddp):
                        for block in range(num_blocks):
                            for page in range(num_pages_per_block):
                                full = self.read_page_and_oob(ddp, blocks_offset + block, page)

                                data = full[0:self.page_size]
                                spare = full[self.page_size:]
                                assert len(data) == self.page_size
                                assert len(spare) == self.oob_size

                                onenand_bin.write(data)
                                onenand_oob.write(spare)

                                bar.update(chunk)

    def dump_flexnand(self):
        if self.slc_blocks > 0:
            print("Dumping OneNAND & OOB [SLC]")
            self._dump_blocks_pages("onenand_slc", self.slc_blocks, 0, SLC_PAGES_PER_BLOCK)

        if self.mlc_blocks > 0:
            print("Dumping OneNAND & OOB [MLC]")
            self._dump_blocks_pages("onenand_mlc", self.mlc_blocks, self.slc_blocks, MLC_PAGES_PER_BLOCK)

    def dump_onenand_slc(self):
        print("Dumping OneNAND & OOB")
        self._dump_blocks_pages("onenand", self.blocks, 0, SLC_PAGES_PER_BLOCK)

    def execute(self, dev, output):
        super().execute(dev, output)

        self.output = output

        print("=" * 80)

        device_id = self.readh(self.onenand_DEVICE_ID)
        print("DeviceID: {:04X}".format(device_id))

        ddp = (device_id >> 3) & 0b1
        density = (device_id >> 4) & 0b111
        separation = (device_id >> 8) & 0b11

        print("* DeviceID [3]    Single/DDP:    {:0b}   = {}".format(ddp, deviceid_ddp[ddp]))
        print("* DeviceID [6:4]  Density:       {:03b} = {}".format(density, deviceid_density[density]))
        print("* DeviceID [9:8]  Separation:    {:02b}  = {}".format(separation, deviceid_separation[separation]))

        print("=" * 80)

        # size excluding oob and before flex gets split into SLC/MLC
        usable_raw_size = raw_sizes[density]

        if separation == SEPARATION_FLEX:
            assert not ddp

            self.num_ddp = 1

            self.page_size = 4096
            self.oob_size = 128

            if self.opts.get("fully_slc", False):
                pi = -1
                boundary_address = -1
                self.mlc_blocks = 0
                self.slc_blocks = usable_raw_size // (MLC_PAGES_PER_BLOCK * self.page_size)
            else:
                print("Readout Partition Information...")
                pi = self.read_pi(0)

                if pi == 0xFFFF:
                    print("WARNING: PI is 0xFFFF - this device might be fully SLC. Please run mlc_check.")

                boundary_address = pi & 0b1111111111

                self.slc_blocks = boundary_address + 1
                # calculate mlc blocks as taking whole device as mlc then subtract the slc blocks
                self.mlc_blocks = usable_raw_size // (MLC_PAGES_PER_BLOCK * self.page_size) - self.slc_blocks

            print("Partition Information: 0x{:04X} | Boundary Address: 0x{:X} | SLC blocks: 0x{:X} ({} MiB) | MLC blocks: 0x{:X} ({} MiB)".format(
                pi, boundary_address,
                self.slc_blocks, SLC_PAGES_PER_BLOCK*self.page_size*self.slc_blocks//1024//1024,
                self.mlc_blocks, MLC_PAGES_PER_BLOCK*self.page_size*self.mlc_blocks//1024//1024))

            print("Page Architecture: {}b Page | {}b OOB".format(self.page_size, self.oob_size))
            self.dump_flexnand()
        elif separation == SEPARATION_SLC:
            self.num_ddp = int(ddp) + 1

            has_4k_pages = False

            if "has_4k_pages" in self.opts:
                has_4k_pages = self.opts["has_4k_pages"]
            else:
                # assume 4k pages for devices that are 2Gb or higher raw size per ddp chip
                # e.g. 512MB w/o ddp would be 4k page, but 512MB with ddp would be 2k page
                has_4k_pages = (usable_raw_size // self.num_ddp) >= 512 * 1024 * 1024

            if has_4k_pages:
                self.page_size = 4096
                self.oob_size = 128
            else:
                self.page_size = 2048
                self.oob_size = 64

            self.blocks = usable_raw_size // (SLC_PAGES_PER_BLOCK * self.page_size)
            self.blocks //= self.num_ddp

            print("Page Architecture: {}b Page | {}b OOB".format(self.page_size, self.oob_size))
            self.dump_onenand_slc()
        else:
            raise RuntimeError("unsupported configuration for CommonOnenandDumper")
