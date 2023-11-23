from device import Device
from dump.nec_protocol import SLOW_READ

from dump.nec_memory_dumper import NecMemoryDumper
from dump.nec_nand_dumper import NecNandDumper
from dump.nec_onenand_dumper import NecOnenandDumper
from dump.nec_memory_dumper_payload import NecMemoryDumperPayload
from dump.nec_nand_id import NecNandId
from dump.nec_nand_dumper_lp import NecNandDumperLp
from dump.nec_nand_dumper_lp_via_poke import NecNandDumperLpViaPoke
from dump.pipl_exploit_memory_dumper import PiplExploitMemoryDumper
from dump.pipl_onenand_dumper import PiplOnenandDumper
from dump.pipl_onenand_id import PiplOnenandId
from dump.pipl_onenand_fast import PiplOnenandFast


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

    Device("p900iv", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(32)),
        "dump_nand": NecNandDumper(size=MB(32)),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),

    Device("n701i", 0x0409, 0x0142, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(64), quirks=SLOW_READ),
    }, payload_base=0x10000000, onenand_addr=0x06000000),

    Device("p851i", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(32), big=1),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),

    Device("n901is", 0x0409, 0x0144, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(64), quirks=SLOW_READ),
    }, payload_base=0x10000000, onenand_addr=0x06000000),

    Device("p901is", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x0C000000, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(64), big=1),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),

    Device("p702i", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x08000000, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x10000000, quirks=SLOW_READ),

    Device("p902i", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x08000000, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x10000000, quirks=SLOW_READ),

    Device("p903i", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x90000000, onenand_addr=0x08000000),

    Device("p704i", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(96)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x90000000, onenand_addr=0x08000000),

    Device("n-01a", 0x0409, 0x0240, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5198, usb_data=0x33ef51e2, usb_datasz=0x33ef51dc, usb_respfunc=0x5098,
       quirks=SLOW_READ),

    Device("n-02a", 0x0409, 0x025c, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nor_slow": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
        "nand_id": NecNandId(),
        "dump_nand_slow": NecNandDumperLpViaPoke(),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5198, usb_data=0x33ef51e2, usb_datasz=0x33ef51dc, usb_respfunc=0x519c,
       quirks=SLOW_READ),

    Device("p-01a", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
    }, exploit_flavor="A"),

    Device("p-03a", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
    }, exploit_flavor="A"),

    Device("p-04a", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
    }, exploit_flavor="A"),

    Device("p-10a", 0x04da, 0x216b, {
        "dump_nor": PiplExploitMemoryDumper(base=0x0, size=MB(128)),
        "onenand_id": PiplOnenandId(),
        "dump_nand": PiplOnenandDumper(size=MB(256)),
    }, exploit_flavor="A", payload_base=0x8009c000, onenand_addr=0x0C000000),

    Device("p-01b", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand_1": PiplOnenandDumper(onenand_addr=0x0C000000, size=MB(256)),
        "dump_nand_2": PiplOnenandDumper(onenand_addr=0x18000000, size=MB(256)),
    }, exploit_flavor="B", payload_base=0x83800000),

    Device("p-02b", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand_1": PiplOnenandDumper(onenand_addr=0x0C000000, size=MB(256)),
        "dump_nand_2": PiplOnenandDumper(onenand_addr=0x18000000, size=MB(256)),
    }, exploit_flavor="B", payload_base=0x83800000),

    Device("p-03b", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
    }, exploit_flavor="B"),

    Device("p-04b", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
    }, exploit_flavor="B"),

    Device("p-07b", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
    }, exploit_flavor="B"),

    Device("p-06c", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand_peek_poke": PiplOnenandDumper(has_4k_pages=True, size=MB(1024)),
        "dump_nand": PiplOnenandFast(size=MB(1024)),
        "onenand_id": PiplOnenandId(),
    }, exploit_flavor="C", payload_base=0x83800000, onenand_addr=0x0C000000,
       usb_command=0x8115a960, usb_data=0x8115a54a, usb_datasz=0x8115a544, usb_respfunc=0x80027f6c),

    Device("p-01f", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
    }, exploit_flavor="C"),

    Device("p-01g", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
    }, exploit_flavor="C"),

    Device("p-01h", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
    }, exploit_flavor="C"),
]
