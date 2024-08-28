import tqdm
import struct

from dump.nec_protocol import NecProtocol
from dump.nec_pipl_rw_access import NecPiplRwAccess


class NecGpmc(NecPiplRwAccess, NecProtocol):

    def execute(self, dev, output):
        super().execute(dev, output)

        for x in range(8):
            config1 = self.readw(0x6E000060 + x * 0x30)
            config7 = self.readw(0x6E000078 + x * 0x30)

            muxadddata = (config1 >> 9) & 0b1
            devicetype = (config1 >> 10) & 0b11
            devicesize = (config1 >> 12) & 0b11
            csvalid = bool(config7 & 0b1000000)
            baseaddress = config7 & 0b111111

            print("GPMC{} | MUXADDDATA {} DEVICETYPE {} DEVICESIZE {} CSVALID {} BASEADDRESS 0x{:02X}".format(
                x,
                muxadddata, devicetype, devicesize,
                int(csvalid), baseaddress))
