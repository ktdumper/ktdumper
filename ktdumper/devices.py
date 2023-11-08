from device import Device
from dump.nec_memory_dumper import NecMemoryDumper
from dump.nec_nand_dumper import NecNandDumper
from dump.nec_onenand_dumper import NecOnenandDumper
from dump.nec_protocol import SLOW_READ


def MB(x):
    return x*1024*1024


DEVICES = [
    Device("n900i", 0x0409, 0x0112, {
        "dump_nor": NecMemoryDumper("dump_nor.bin", 0x0, MB(32)),
        "dump_nand": NecNandDumper(size=MB(32), quirks=SLOW_READ),
    }),
    Device("n900is", 0x0409, 0x0121, {
        "dump_nor": NecMemoryDumper("dump_nor.bin", 0x0, MB(64)),
        "dump_nand": NecNandDumper(size=MB(32)),
    }),
    Device("n901is", 0x0409, 0x0144, {
        "dump_nor": NecMemoryDumper("dump_nor.bin", 0x0, MB(64)),
        "dump_nand": NecOnenandDumper(payload_base=0x10000000, onenand_addr=0x06000000, size=MB(64), quirks=SLOW_READ),
    }),
    Device("p900iv", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper("dump_nor.bin", 0x0, MB(32), quirks=SLOW_READ),
        "dump_nand": NecNandDumper(size=MB(32), quirks=SLOW_READ),
    }),
    Device("p901is", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper("dump_rom.bin", 0x0, 0x8000),
        "dump_nor": NecMemoryDumper("dump_nor.bin", 0x0C000000, MB(64), quirks=SLOW_READ),
        "dump_nand": NecNandDumper(size=MB(64), big=1, quirks=SLOW_READ),
    }),
    Device("p902i", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper("dump_rom.bin", 0x0, 0x8000),
        "dump_nor": NecMemoryDumper("dump_nor.bin", 0x08000000, MB(64), quirks=SLOW_READ),
        "dump_nand": NecOnenandDumper(size=MB(128), quirks=SLOW_READ),
    }),
]
