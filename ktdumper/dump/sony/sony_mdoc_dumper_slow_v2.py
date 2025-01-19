# based on https://lwn.net/Articles/246158/

import struct
import math
import tqdm
from dump.sony.sony_protocol_v2 import SonyProtocol_v2
from dump.v2.rw_access_v2 import RwAccess_v2

DOCH_IDENTIFY_DISKONCHIP_DEVICE = 0x00
DOCH_PARTITION_MANAGEMENT = 0xfa
DOCH_EXT_DEVICE_CTRL = 0xfc

DOCH_GET_PARTITION_INFO = 0x00

DOCH_ATA_REGS_OFFSET_8KB = 0x0800
DOCH_ATA_DATA_OFFSET_8KB = 0x1000
DOCH_CONF_REGS_OFFSET_8KB = 0x1400

DOCH_CHIP_ID1 = 0x00
DOCH_CHIP_ID2 = 0x22

DOCH_ATA_DATA = 0x00
DOCH_ATA_ERROR = 0x02
DOCH_ATA_NSECTOR = 0x04
DOCH_SECTOR_NO_REG = 0x06
DOCH_CYLINDER_LOW_REG  = 0x08
DOCH_CYLINDER_HIGH_REG = 0x0A
DOCH_DRIVE_HEAD_REG = 0x0C
DOCH_ATA_STATUS = 0x0E
DOCH_ATA_FEATURE = DOCH_ATA_ERROR
DOCH_ATA_COMMAND = DOCH_ATA_STATUS

DOCH_VSCMD_READ_PARTITION = 0x82
DOCH_LBA = 0x40

SECTOR_SIZE = 512


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s%s" % (s, size_name[i])


class SonyMdocDumperSlow_v2(RwAccess_v2, SonyProtocol_v2):

    def parse_opts(self, opts):
        super().parse_opts(opts)

        self.mdoc_base = opts["mdoc_base"]

        self.reg_DOCH_CHIP_ID1 = self.mdoc_base + DOCH_CONF_REGS_OFFSET_8KB + DOCH_CHIP_ID1
        self.reg_DOCH_CHIP_ID2 = self.mdoc_base + DOCH_CONF_REGS_OFFSET_8KB + DOCH_CHIP_ID2

        self.reg_DOCH_ATA_STATUS = self.mdoc_base + DOCH_ATA_REGS_OFFSET_8KB + DOCH_ATA_STATUS
        self.reg_DOCH_ATA_DATA = self.mdoc_base + DOCH_ATA_REGS_OFFSET_8KB + DOCH_ATA_DATA
        self.reg_DOCH_ATA_FEATURE = self.mdoc_base + DOCH_ATA_REGS_OFFSET_8KB + DOCH_ATA_FEATURE
        self.reg_DOCH_ATA_COMMAND = self.mdoc_base + DOCH_ATA_REGS_OFFSET_8KB + DOCH_ATA_COMMAND
        self.reg_DOCH_ATA_NSECTOR = self.mdoc_base + DOCH_ATA_REGS_OFFSET_8KB + DOCH_ATA_NSECTOR
        self.reg_DOCH_SECTOR_NO_REG = self.mdoc_base + DOCH_ATA_REGS_OFFSET_8KB + DOCH_SECTOR_NO_REG
        self.reg_DOCH_CYLINDER_LOW_REG = self.mdoc_base + DOCH_ATA_REGS_OFFSET_8KB + DOCH_CYLINDER_LOW_REG
        self.reg_DOCH_CYLINDER_HIGH_REG = self.mdoc_base + DOCH_ATA_REGS_OFFSET_8KB + DOCH_CYLINDER_HIGH_REG
        self.reg_DOCH_DRIVE_HEAD_REG = self.mdoc_base + DOCH_ATA_REGS_OFFSET_8KB + DOCH_DRIVE_HEAD_REG

    def wait_ready(self):
        while True:
            ret = self.readb(self.reg_DOCH_ATA_STATUS)
            # print("DOCH_ATA_STATUS: 0x{:X}".format(ret))
            if ret == 0x58 or ret == 0x50:
                break

    def read_words(self, num_words):
        out = b""
        for x in range(num_words):
            out += struct.pack("<H", self.readh(self.reg_DOCH_ATA_DATA))
        return out

    def get_device_info(self):
        self.writeb(DOCH_IDENTIFY_DISKONCHIP_DEVICE, self.reg_DOCH_ATA_FEATURE)
        self.writeb(DOCH_EXT_DEVICE_CTRL, self.reg_DOCH_ATA_COMMAND)
        self.wait_ready()
        blk = self.read_words(SECTOR_SIZE//2)
        self.wait_ready()

        num_parts = struct.unpack_from("<H", blk[0x7c:])[0]
        return num_parts

    def get_part_info(self, part):
        self.writeb(part, self.reg_DOCH_ATA_NSECTOR)
        self.writeb(DOCH_GET_PARTITION_INFO, self.reg_DOCH_ATA_FEATURE)
        self.writeb(DOCH_PARTITION_MANAGEMENT, self.reg_DOCH_ATA_COMMAND)
        self.wait_ready()
        part_info = self.read_words(SECTOR_SIZE//2)
        self.wait_ready()

        part_sectors = struct.unpack_from("<I", part_info[16:])[0]
        return part_sectors

    def read_sector(self, part, sector):
        self.wait_ready()
        self.writeb(1, self.reg_DOCH_ATA_NSECTOR)
        self.writeb(sector & 0xFF, self.reg_DOCH_SECTOR_NO_REG)
        self.writeb((sector >> 8) & 0xFF, self.reg_DOCH_CYLINDER_LOW_REG)
        self.writeb((sector >> 16) & 0xFF, self.reg_DOCH_CYLINDER_HIGH_REG)
        self.writeb(part, self.reg_DOCH_ATA_FEATURE)
        self.writeb(((sector >> 24) & 0x0F) | DOCH_LBA, self.reg_DOCH_DRIVE_HEAD_REG)
        self.writeb(DOCH_VSCMD_READ_PARTITION, self.reg_DOCH_ATA_COMMAND)
        self.wait_ready()
        return self.read_words(SECTOR_SIZE//2)

    def execute(self, dev, output):
        super().execute(dev, output)

        assert self.readh(self.reg_DOCH_CHIP_ID1) == 0x4833
        assert self.readh(self.reg_DOCH_CHIP_ID2) == 0xb7cc

        num_parts = self.get_device_info()
        print("Detected {} partitions".format(num_parts))
        print("-" * 80)

        sectors = []
        for part in range(num_parts):
            part_sectors = self.get_part_info(part)
            sectors.append(part_sectors)
            print("Partition {} : {}".format(part, convert_size(part_sectors * SECTOR_SIZE)))
        print("-" * 80)

        for part, num_sectors in enumerate(sectors):
            fname = "part_{:02}.bin".format(part)
            print("Dumping {}".format(fname))
            with self.output.mkfile(fname) as nand_bin:
                with tqdm.tqdm(total=SECTOR_SIZE*num_sectors, unit='B', unit_scale=True, unit_divisor=1024) as bar:
                    for sector in range(num_sectors):
                        data = self.read_sector(part, sector)
                        assert len(data) == SECTOR_SIZE

                        nand_bin.write(data)
                        bar.update(len(data))
