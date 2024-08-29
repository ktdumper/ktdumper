from dump.nec_protocol_v2 import NecProtocol_v2
from dump.nec_rw_access_v2 import NecRwAccess_v2
from dump.common_onenand_id import CommonOnenandIdMixin, deviceid_ddp, deviceid_density, deviceid_separation

import struct
import tqdm


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

SLC_PAGES = 64
MLC_PAGES = 128

class NecOnenandFast_v2(CommonOnenandIdMixin, NecRwAccess_v2, NecProtocol_v2):

    def read_page_and_oob(self, block, page):
        try:
            self.usb_send(struct.pack("<BII", 0x71, block, page))
            data = self.usb_receive()
        except Exception:
            print("exception reading block=0x{:X} page=0x{:X}".format(block, page))
            raise

        assert len(data) == self.page_size + self.oob_size
        return data

    def dump_flexnand(self):
        assert self.slc_blocks > 0
        assert self.mlc_blocks > 0

        print("Dumping OneNAND & OOB [SLC]")
        with self.output.mkfile("onenand_slc.bin") as onenand_bin:
            with self.output.mkfile("onenand_slc.oob") as onenand_oob:
                chunk = self.page_size + self.oob_size
                with tqdm.tqdm(total=chunk*SLC_PAGES*self.slc_blocks, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                    for block in range(self.slc_blocks):
                        for page in range(SLC_PAGES):
                            full = self.read_page_and_oob(block, page)

                            data = full[0:self.page_size]
                            spare = full[self.page_size:]
                            assert len(data) == self.page_size
                            assert len(spare) == self.oob_size

                            onenand_bin.write(data)
                            onenand_oob.write(spare)

                            bar.update(chunk)

        print("Dumping OneNAND & OOB [MLC]")
        with self.output.mkfile("onenand_mlc.bin") as onenand_bin:
            with self.output.mkfile("onenand_mlc.oob") as onenand_oob:
                chunk = self.page_size + self.oob_size
                with tqdm.tqdm(total=chunk*MLC_PAGES*self.mlc_blocks, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                    for block in range(self.mlc_blocks):
                        for page in range(MLC_PAGES):
                            full = self.read_page_and_oob(self.slc_blocks + block, page)

                            data = full[0:self.page_size]
                            spare = full[self.page_size:]
                            assert len(data) == self.page_size
                            assert len(spare) == self.oob_size

                            onenand_bin.write(data)
                            onenand_oob.write(spare)

                            bar.update(chunk)

    def execute(self, dev, output):
        super().execute(dev, output)

        self.usb_send(struct.pack("<BI", 0x70, self.onenand_addr))

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

            print("Readout Partition Information...")
            pi = self.read_pi(0)

            boundary_address = pi & 0b1111111111

            self.slc_blocks = boundary_address + 1
            # calculate mlc blocks as taking whole device as mlc then subtract the slc blocks
            self.mlc_blocks = usable_raw_size // (MLC_PAGES * self.page_size) - self.slc_blocks

            print("Partition Information: 0x{:04X} | Boundary Address: 0x{:X} | SLC blocks: 0x{:X} ({} MiB) | MLC blocks: 0x{:X} ({} MiB)".format(
                pi, boundary_address,
                self.slc_blocks, SLC_PAGES*self.page_size*self.slc_blocks//1024//1024,
                self.mlc_blocks, MLC_PAGES*self.page_size*self.mlc_blocks//1024//1024))
            self.dump_flexnand()
        else:
            raise RuntimeError("unsupported configuration for NecOnenandFast_v2")
