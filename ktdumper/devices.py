from device import Device
from dump.nec_protocol import SLOW_READ

from dump.nec_memory_dumper import NecMemoryDumper
from dump.nec_nand_dumper import NecNandDumper
from dump.nec_onenand_dumper import NecOnenandDumper
from dump.nec_memory_dumper_payload import NecMemoryDumperPayload
from dump.nec_nand_id import NecNandId
from dump.nec_nand_dumper_lp import NecNandDumperLp
from dump.nec_nand_dumper_lp_via_poke import NecNandDumperLpViaPoke


def MB(x):
    return x*1024*1024


DEVICES = [
    Device("n900i", 0x0409, 0x0112, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(32)),
        "dump_nand": NecNandDumper(size=MB(32), quirks=SLOW_READ),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400),

    Device("n900is", 0x0409, 0x0121, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(32), quirks=SLOW_READ),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400),

    Device("n901is", 0x0409, 0x0144, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(64), quirks=SLOW_READ),
    }, payload_base=0x10000000, onenand_addr=0x06000000),

    Device("n-02a", 0x0409, 0x025c, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nor_slow": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
        "nand_id": NecNandId(),
        "dump_nand_slow": NecNandDumperLpViaPoke(),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5198, usb_data=0x33ef51e2, usb_datasz=0x33ef51dc, usb_respfunc=0x519c,
       quirks=SLOW_READ),

    Device("p702i", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x08000000, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x10000000, quirks=SLOW_READ),

    Device("p900iv", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(32)),
        "dump_nand": NecNandDumper(size=MB(32)),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),

    Device("p901is", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x0C000000, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(64), big=1),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),

    Device("p902i", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x08000000, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x10000000, quirks=SLOW_READ),

    Device("p903i", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x90000000, onenand_addr=0x08000000),
]
