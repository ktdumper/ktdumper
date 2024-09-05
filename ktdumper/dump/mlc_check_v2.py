from dump.onenand_fast_v2 import raw_sizes
from dump.common_onenand_id import CommonOnenandIdMixin, deviceid_ddp, deviceid_density, deviceid_separation

import struct
import tqdm


class MlcCheck_v2(CommonOnenandIdMixin):

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

        pi = self.read_pi(0)
        boundary_address = pi & 0b1111111111

        usable_raw_size = raw_sizes[density]

        blocks = usable_raw_size // (128 * 4096)

        mapping = []
        for blk in tqdm.tqdm(range(blocks)):
            self.usb_send(struct.pack("<BI", 0x71, blk))
            resp = self.usb_receive()
            mapping.append(resp[0])

        num_slc_blocks = 0
        while num_slc_blocks < len(mapping) and mapping[num_slc_blocks]:
            num_slc_blocks += 1

        num_mlc_blocks = len(mapping) - num_slc_blocks

        print("Total device blocks: 0x{:X}".format(len(mapping)))
        print("Likely SLC blocks: 0x{:X} | Likely MLC blocks: 0x{:X}".format(num_slc_blocks, num_mlc_blocks))
        print("Raw data: {}".format("".join(map(str, mapping))))

        if boundary_address+1 == num_slc_blocks:
            print("Matches PI!")
        else:
            print("Does NOT match PI!")
