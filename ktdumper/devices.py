from device import Device
from dump.nec_memory_dumper import NecMemoryDumper
from dump.nec_nand_dumper import NecNandDumper
from dump.nec_protocol import SLOW_READ


def MB(x):
    return x*1024*1024


DEVICES = [
    Device("p901is", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper("dump_rom.bin", 0x0, 0x8000),
        "dump_nor": NecMemoryDumper("dump_nor.bin", 0x0C000000, MB(64), quirks=SLOW_READ),
        "dump_nand": NecNandDumper(size=MB(64), quirks=SLOW_READ),
    }),
]
