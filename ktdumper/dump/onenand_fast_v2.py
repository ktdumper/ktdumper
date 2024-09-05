from dump.common_onenand_id import CommonOnenandIdMixin, deviceid_ddp, deviceid_density, deviceid_separation

import struct
import tqdm

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

class OnenandFast_v2(CommonOnenandIdMixin):

    def read_page_and_oob(self, block, page):
        try:
            self.usb_send(struct.pack("<BII", self.onenand_cmd, block, page))
            data = self.usb_receive()
        except Exception:
            print("exception reading block=0x{:X} page=0x{:X}".format(block, page))
            raise

        assert len(data) == self.page_size + self.oob_size
        return data

    def _dump_blocks_pages(self, prefixname, num_blocks, blocks_offset, num_pages_per_block):
        with self.output.mkfile(prefixname + ".bin") as onenand_bin:
            with self.output.mkfile(prefixname + ".oob") as onenand_oob:
                chunk = self.page_size + self.oob_size
                with tqdm.tqdm(total=chunk*num_pages_per_block*num_blocks, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                    for block in range(num_blocks):
                        for page in range(num_pages_per_block):
                            full = self.read_page_and_oob(blocks_offset + block, page)

                            data = full[0:self.page_size]
                            spare = full[self.page_size:]
                            assert len(data) == self.page_size
                            assert len(spare) == self.oob_size

                            onenand_bin.write(data)
                            onenand_oob.write(spare)

                            bar.update(chunk)

    def dump_flexnand(self):
        self.onenand_cmd = 0x70

        if self.slc_blocks > 0:
            print("Dumping OneNAND & OOB [SLC]")
            self._dump_blocks_pages("onenand_slc", self.slc_blocks, 0, SLC_PAGES_PER_BLOCK)

        if self.mlc_blocks > 0:
            print("Dumping OneNAND & OOB [MLC]")
            self._dump_blocks_pages("onenand_mlc", self.mlc_blocks, self.slc_blocks, MLC_PAGES_PER_BLOCK)

    def dump_onenand_2k(self):
        self.onenand_cmd = 0x72

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

            self.page_size = 4096
            self.oob_size = 128
            self.inline_spare = True

            if self.opts.get("fully_slc", False):
                pi = -1
                boundary_address = -1
                self.mlc_blocks = 0
                self.slc_blocks = usable_raw_size // (MLC_PAGES_PER_BLOCK * self.page_size)
            else:
                print("Readout Partition Information...")
                pi = self.read_pi(0)

                boundary_address = pi & 0b1111111111

                self.slc_blocks = boundary_address + 1
                # calculate mlc blocks as taking whole device as mlc then subtract the slc blocks
                self.mlc_blocks = usable_raw_size // (MLC_PAGES_PER_BLOCK * self.page_size) - self.slc_blocks

            print("Partition Information: 0x{:04X} | Boundary Address: 0x{:X} | SLC blocks: 0x{:X} ({} MiB) | MLC blocks: 0x{:X} ({} MiB)".format(
                pi, boundary_address,
                self.slc_blocks, SLC_PAGES_PER_BLOCK*self.page_size*self.slc_blocks//1024//1024,
                self.mlc_blocks, MLC_PAGES_PER_BLOCK*self.page_size*self.mlc_blocks//1024//1024))
            self.dump_flexnand()
        elif separation == SEPARATION_SLC:
            # TODO: only supports 2k pages, non-DDP right now

            assert not ddp

            self.page_size = 2048
            self.oob_size = 64
            self.inline_spare = False

            self.blocks = usable_raw_size // (SLC_PAGES_PER_BLOCK * self.page_size)
            self.dump_onenand_2k()
        else:
            raise RuntimeError("unsupported configuration for OnenandFast_v2")
