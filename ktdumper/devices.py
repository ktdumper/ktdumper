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
from dump.pipl_emmc_dumper import PiplEmmcDumper
from dump.sh_exploit import ShExploit
from dump.fujitsu_java_dumper import FujitsuJavaDumper
from dump.pipl_emmc_fuse import PiplEmmcFuse
from dump.sh_srec_exploit_mlba_dumper import ShSrecExploitMlbaDumper
from dump.sh_srec_exploit_memory_dumper import ShSrecExploitMemoryDumper
from dump.sh_srec_exploit_nand_id import ShSrecExploitNandId
from dump.sh_srec_exploit_nand_dumper import ShSrecExploitNandDumper
from dump.sh_srec_exploit_onenand_id import ShSrecExploitOnenandId
from dump.sh_srec_exploit_onenand_dumper import ShSrecExploitOnenandDumper


def MB(x):
    return x*1024*1024


DEVICES = [
    ################################################################################################
    # CASIO
    ################################################################################################

    Device("830ca", 0x1967, 0x2002, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee50dc, usb_data= 0x33ef5126, usb_datasz=0x33ef5120, usb_respfunc=0x5910,
       quirks=SLOW_READ),

    Device("930ca", 0x1967, 0x2004, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee51a8, usb_data=0x33ef51f2, usb_datasz=0x33ef51ec, usb_respfunc=0x50a8,
       quirks=SLOW_READ),

    ################################################################################################
    # NEC
    ################################################################################################

    # DOCOMO

    Device("n900i", 0x0409, 0x0112, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(32)),
        "dump_nand": NecNandDumper(size=MB(32), quirks=SLOW_READ),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400),

    Device("n900is", 0x0409, 0x0121, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(32), quirks=SLOW_READ),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400),

    Device("n901ic", 0x0409, 0x0129, {
        "dump_nor": NecMemoryDumper(base=0x04000000, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(64), quirks=SLOW_READ, big=1),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400),

    Device("n901is", 0x0409, 0x0144, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(64), quirks=SLOW_READ),
    }, payload_base=0x10000000, onenand_addr=0x06000000),

    Device("n701i", 0x0409, 0x0142, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(64), quirks=SLOW_READ),
    }, payload_base=0x10000000, onenand_addr=0x06000000),

    Device("n902i", 0x0409, 0x014c, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x10000000, quirks=SLOW_READ),

    Device("n702id", 0x0409, 0x0168, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(64), quirks=SLOW_READ),
    }, payload_base=0x10000000, onenand_addr=0x06000000),

    Device("n904i", 0x0409, 0x0200, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x08000000, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x06000000, quirks=SLOW_READ),

    Device("n905i", 0x0409, 0x0210, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33eec3f8, usb_data=0x33efc442, usb_datasz=0x33efc43c, usb_respfunc=0x4f58,
       quirks=SLOW_READ),

    Device("n905imyu", 0x0409, 0x0220, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33eec400, usb_data=0x33efc44a, usb_datasz=0x33efc444, usb_respfunc=0x4f94,
       quirks=SLOW_READ),

    Device("n706i", 0x0409, 0x023c, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee50d0, usb_data=0x33ef511a, usb_datasz=0x33ef5114, usb_respfunc=0x582c,
       quirks=SLOW_READ),

    Device("n706ie", 0x0409, 0x024a, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x00000000, size=MB(128)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee50d0, usb_data=0x33ef511a, usb_datasz=0x33ef5114, usb_respfunc=0x582c,
       quirks=SLOW_READ),

    Device("n706i2", 0x0409, 0x0224, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee50d0, usb_data=0x33ef511a, usb_datasz=0x33ef5114, usb_respfunc=0x5520,
       quirks=SLOW_READ),

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

    Device("n-03a", 0x0409, 0x0268, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee50d0, usb_data=0x33ef511a, usb_datasz=0x33ef5114, usb_respfunc=0x582c,
       quirks=SLOW_READ),

    Device("n-04a", 0x0409, 0x0260, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5198, usb_data=0x33ef51e2, usb_datasz=0x33ef51dc, usb_respfunc=0x50a8,
       quirks=SLOW_READ),

    Device("n-06a", 0x0409, 0x0274, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5198, usb_data=0x33ef51e2, usb_datasz=0x33ef51dc, usb_respfunc=0x50e8,
       quirks=SLOW_READ),

    Device("n-07a", 0x0409, 0x0280, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5198, usb_data=0x33ef51e2, usb_datasz=0x33ef51dc, usb_respfunc=0x50f0,
       quirks=SLOW_READ),

    Device("n-08a", 0x0409, 0x026c, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5198, usb_data=0x33ef51e2, usb_datasz=0x33ef51dc, usb_respfunc=0x50e8,
       quirks=SLOW_READ),

    Device("n-03b", 0x0409, 0x02a0, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5198, usb_data=0x33ef51e2, usb_datasz=0x33ef51dc, usb_respfunc=0x50d8,
       quirks=SLOW_READ),

    # SOFTBANK

    Device("820n", 0x0409, 0x0250, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nor_slow": NecMemoryDumper(base=0x0, size=MB(128)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33eec3f8, usb_data=0x33efc442, usb_datasz=0x33efc43c, usb_respfunc=0x4f58,
       quirks=SLOW_READ),

    Device("930n", 0x0409, 0x027c, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5190, usb_data=0x33ef51da, usb_datasz=0x33ef51d4, usb_respfunc=0x50d4,
       quirks=SLOW_READ),

    Device("831n", 0x0409, 0x0284, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee50c4, usb_data=0x33ef510e, usb_datasz=0x33ef5108, usb_respfunc=0x57dc,
       quirks=SLOW_READ),

    ################################################################################################
    # PANASONIC
    ################################################################################################

    # DOCOMO

    Device("p900i", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(32)),
        "dump_nand": NecNandDumper(size=MB(32)),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),

    Device("p900iv", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(32)),
        "dump_nand": NecNandDumper(size=MB(32)),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),

    Device("p700i", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x0C000000, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(64), big=1),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),

    Device("p901i", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x0C000000, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(64), big=1),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),

    Device("p901is", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x0C000000, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(64), big=1),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),

    Device("p901itv", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x90000000, onenand_addr=0x08000000, quirks=SLOW_READ),

    Device("p851i", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(32), big=1),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),

    Device("p902i", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x08000000, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x10000000, quirks=SLOW_READ),

    Device("p902is", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x08000000, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x10000000, quirks=SLOW_READ),

    Device("p702i", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x08000000, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x10000000, quirks=SLOW_READ),

    Device("p702id", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x08000000, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x10000000, quirks=SLOW_READ),

    Device("p903i", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x90000000, onenand_addr=0x08000000),

    Device("p903itv", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(256)),
    }, payload_base=0x90000000, onenand_addr=0x0C000000),

    Device("p904i", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(512), has_ddp=True),
    }, payload_base=0x90040000, onenand_addr=0x0C000000),

    Device("p704i", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(96)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x90000000, onenand_addr=0x08000000),

    Device("p-01a", 0x04da, 0x216b, {
        "dump_nor": PiplExploitMemoryDumper(base=0x0, size=MB(128)),
        "onenand_id": PiplOnenandId(),
        "dump_nand": PiplOnenandDumper(size=MB(512), has_ddp=True),
    }, exploit_flavor="A", payload_base=0x8009c000, onenand_addr=0x0C000000),

    Device("p-03a", 0x04da, 0x216b, {
        "dump_nor": PiplExploitMemoryDumper(base=0x0, size=MB(128)),
        "onenand_id": PiplOnenandId(),
        "dump_nand": PiplOnenandDumper(size=MB(256)),
    }, exploit_flavor="A", payload_base=0x8009c000, onenand_addr=0x0C000000),

    Device("p-04a", 0x04da, 0x216b, {
        "dump_nor": PiplExploitMemoryDumper(base=0x0, size=MB(128)),
        "onenand_id": PiplOnenandId(),
        "dump_nand": PiplOnenandDumper(size=MB(256)),
    }, exploit_flavor="A", payload_base=0x8009c000, onenand_addr=0x0C000000),

    Device("p-10a", 0x04da, 0x216b, {
        "dump_nor": PiplExploitMemoryDumper(base=0x0, size=MB(128)),
        "onenand_id": PiplOnenandId(),
        "dump_nand": PiplOnenandDumper(size=MB(256)),
    }, exploit_flavor="A", payload_base=0x8009c000, onenand_addr=0x0C000000),

    Device("p-01b", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand_a": PiplOnenandDumper(onenand_addr=0x0C000000, size=MB(512), has_ddp=True),
        "dump_nand_b": PiplOnenandDumper(onenand_addr=0x18000000, size=MB(256)),
    }, exploit_flavor="B", payload_base=0x83800000),

    Device("p-02b", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "onenand_id_a": PiplOnenandId(onenand_addr=0x0C000000),
        "onenand_id_b": PiplOnenandId(onenand_addr=0x18000000),
        "dump_nand_a": PiplOnenandDumper(onenand_addr=0x0C000000, size=MB(512), has_ddp=True),
        "dump_nand_b": PiplOnenandDumper(onenand_addr=0x18000000, size=MB(256)),
    }, exploit_flavor="B", payload_base=0x83800000),

    Device("p-03b", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand": PiplOnenandDumper(size=MB(512), has_ddp=True),
    }, exploit_flavor="B", payload_base=0x83800000, onenand_addr=0x0C000000),

    Device("p-04b", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand_a": PiplOnenandDumper(onenand_addr=0x0C000000, size=MB(512), has_ddp=True),
        "dump_nand_b": PiplOnenandDumper(onenand_addr=0x18000000, size=MB(256)),
    }, exploit_flavor="B", payload_base=0x83800000),

    Device("p-07b", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand": PiplOnenandDumper(size=MB(512)),
        "onenand_id": PiplOnenandId(),
    }, exploit_flavor="B", payload_base=0x83800000, onenand_addr=0x0C000000),

    Device("p-06c", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand_peek_poke": PiplOnenandDumper(has_4k_pages=True, size=MB(1024)),
        "dump_nand": PiplOnenandFast(size=MB(1024)),
        "onenand_id": PiplOnenandId(),
    }, exploit_flavor="C", payload_base=0x83800000, onenand_addr=0x0C000000,
       usb_command=0x8115a960, usb_data=0x8115a54a, usb_datasz=0x8115a544, usb_respfunc=0x80027f6c),

    Device("p-01f", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_emmc": PiplEmmcDumper(size=MB(2048)),
        "fuse_user": PiplEmmcFuse(offset=0x1a800000, size=0x3fe00000),
    }, exploit_flavor="C", payload_base=0x83800000, emmc_read_and_dcache=0x8000dba8, emmc_inv_dcache_and_write=0x8000dc80,
       usb_command=0x8115a960, usb_data=0x8115a54a, usb_datasz=0x8115a544, usb_respfunc=0x80010a1c),

    Device("p-01g", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_emmc": PiplEmmcDumper(size=MB(2048)),
        "fuse_user": PiplEmmcFuse(offset=0x1e500000, size=0x3fe00000),
    }, exploit_flavor="C", payload_base=0x83800000, emmc_read_and_dcache=0x8000dbf4, emmc_inv_dcache_and_write=0x8000dccc,
       usb_command=0x8115a960, usb_data=0x8115a54a, usb_datasz=0x8115a544, usb_respfunc=0x80010a68),

    Device("p-01h", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_emmc": PiplEmmcDumper(size=MB(2048)),
        "fuse_user": PiplEmmcFuse(offset=0x1e500000, size=0x3fe00000),
    }, exploit_flavor="C", payload_base=0x83800000, emmc_read_and_dcache=0x8000dbf4, emmc_inv_dcache_and_write=0x8000dccc,
       usb_command=0x8115a960, usb_data=0x8115a54a, usb_datasz=0x8115a544, usb_respfunc=0x80010a68),

    # SOFTBANK

    Device('930p', 0x04da, 0x216b, {
        'dump_rom': PiplExploitMemoryDumper(base=0x0, size=0x8000),
        'dump_nand': PiplOnenandDumper(onenand_addr=0x0C000000, size=MB(512), has_ddp=True),
    }, exploit_flavor="A", payload_base=0x8009c000),

    Device("940p", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand_a": PiplOnenandDumper(onenand_addr=0x0C000000, size=MB(512), has_ddp=True),
        "dump_nand_b": PiplOnenandDumper(onenand_addr=0x18000000, size=MB(256)),
    }, exploit_flavor="B", payload_base=0x83800000),

    Device("942p", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand_a": PiplOnenandDumper(onenand_addr=0x0C000000, size=MB(512), has_ddp=True),
        "dump_nand_b": PiplOnenandDumper(onenand_addr=0x18000000, size=MB(256)),
    }, exploit_flavor="B", payload_base=0x83800000),

    Device("301p", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x00000000, size=0x8000),
        "dump_emmc": PiplEmmcDumper(size=MB(2048)),
    }, exploit_flavor="C", payload_base=0x83800000, emmc_read_and_dcache=0x8000c528,
       usb_command=0x8115a960, usb_data=0x8115a54a, usb_datasz=0x8115a544, usb_respfunc=0x8000f39c),

    ################################################################################################
    # SHARP
    ################################################################################################

    Device("sh706i", 0x04dd, 0x91f1, {
        "dump_nor": ShSrecExploitMemoryDumper(base=0x30000000, size=MB(128)),
        "nand_id": ShSrecExploitNandId(),
        "dump_nand": ShSrecExploitNandDumper(size=MB(256)),
    }, payload_base=0x64000000, fatal_err=0x646069f4, usb_interrupt=0x64601000, usb_getch=0x6460396c, usb_send=0x64603be4, usb_send_commit=0x646034c0,
        nand_data=0x10000000, nand_addr=0x10000010, nand_cmd=0x10000020),
    
    Device("sh-02a", 0x04dd, 0x925f, {
        "dump_nor": ShSrecExploitMemoryDumper(base=0x30000000, size=MB(128)),
        "nand_id": ShSrecExploitNandId(),
        "dump_nand": ShSrecExploitNandDumper(size=MB(256)),
    }, payload_base=0x64000000, fatal_err=0x646069f4, usb_interrupt=0x64601000, usb_getch=0x6460396c, usb_send=0x64603be4, usb_send_commit=0x646034c0,
        nand_data=0x10000000, nand_addr=0x10000010, nand_cmd=0x10000020),

    Device("sh-02b", 0x04dd, 0x92d6, {
        "dump_nand": ShSrecExploitMlbaDumper(),
        "nand_id": ShSrecExploitNandId(),
    }, payload_base=0xE55B0000, fatal_err=0x60c048dc, usb_interrupt=0x60c02000, usb_getch=0x60c03fa8, usb_send=0x60c041ac, usb_send_commit=0x60c03b28,
        nand_data=0x16000000, nand_addr=0x16000010, nand_cmd=0x16000020),

    Device("sh-06b", 0x04dd, 0x9302, {
        "dump_nand": ShSrecExploitMlbaDumper(),
        "nand_id": ShSrecExploitNandId(),
    }, payload_base=0xE55B0000, fatal_err=0x60c048dc, usb_interrupt=0x60c02000, usb_getch=0x60c03fa8, usb_send=0x60c041ac, usb_send_commit=0x60c03b28,
        nand_data=0x16000000, nand_addr=0x16000010, nand_cmd=0x16000020),

    Device("sh-07f", 0x04dd, 0x9464, {
        "jump_symbian": ShExploit(jump_dst=0x50803630),
    }),

    ################################################################################################
    # FUJITSU
    ################################################################################################

    Device("f902i", 0x04c5, 0x10ce, {"dump_java": FujitsuJavaDumper()}),
    Device("f902is", 0x04c5, 0x10db, {"dump_java": FujitsuJavaDumper()}),
    Device("f702id", 0x04c5, 0x10d9, {"dump_java": FujitsuJavaDumper()}),
    Device("f903ix", 0x04c5, 0x113f, {"dump_java": FujitsuJavaDumper()}),
    Device("f884ies", 0x04c5, 0x1199, {"dump_java": FujitsuJavaDumper()}),
    Device("f904i", 0x04c5, 0x1122, {"dump_java": FujitsuJavaDumper()}),

    Device("f905i", 0x04c5, 0x1128, {
        "dump_java": FujitsuJavaDumper(),
        "dump_nor": ShSrecExploitMemoryDumper(base=0x30000000, size=MB(128)),
        "nand_id": ShSrecExploitNandId(),
        "dump_nand": ShSrecExploitNandDumper(size=MB(256)),
    }, payload_base=0x64000000, fatal_err=0x64606890, usb_interrupt=0x64601000, usb_getch=0x6460380c, usb_send=0x64603a80, usb_send_commit=0x6460339c,
        nand_data=0x10000000, nand_addr=0x10000010, nand_cmd=0x10000020),

    Device("f906i", 0x04c5, 0x115d, {
        "dump_java": FujitsuJavaDumper(),
        "dump_nor": ShSrecExploitMemoryDumper(base=0x30000000, size=MB(128)),
        "onenand_id": ShSrecExploitOnenandId(),
        "dump_nand": ShSrecExploitOnenandDumper(size=MB(256)),
    }, payload_base=0x64000000, fatal_err=0x64606700, usb_interrupt=0x64601000, usb_getch=0x646036cc, usb_send=0x64603940, usb_send_commit=0x6460325c,
        onenand_addr=0x10000000),

    Device("f-04a", 0x04c5, 0x115e, {"dump_java": FujitsuJavaDumper()}),
    Device("f-05a", 0x04c5, 0x1167, {"dump_java": FujitsuJavaDumper()}),
    Device("f-07a", 0x04c5, 0x115f, {"dump_java": FujitsuJavaDumper()}),
    Device("f-10a", 0x04c5, 0x1162, {"dump_java": FujitsuJavaDumper()}),

    Device("f-02b", 0x04c5, 0x11d2, {
        "onenand_id": ShSrecExploitOnenandId(),
        "dump_nand": ShSrecExploitOnenandDumper(size=MB(512), has_4k_pages=True),
    }, payload_base=0xE55B0000, fatal_err=0x60c04848, usb_interrupt=0x60C02000, usb_getch=0x60c03f14, usb_send=0x60c04118, usb_send_commit=0x60c03a94,
        onenand_addr=0x30000000),

    Device("f-03b", 0x04c5, 0x11d8, {
        "onenand_id": ShSrecExploitOnenandId(),
        "dump_nand": ShSrecExploitOnenandDumper(size=MB(512), has_4k_pages=True),
    }, payload_base=0xE55B0000, fatal_err=0x60c04848, usb_interrupt=0x60C02000, usb_getch=0x60c03f14, usb_send=0x60c04118, usb_send_commit=0x60c03a94,
        onenand_addr=0x30000000),

    Device("f-08c", 0x04c5, 0x122f, {
        "onenand_id": ShSrecExploitOnenandId(),
        "dump_nand": ShSrecExploitOnenandDumper(size=MB(512), has_4k_pages=True),
    }, payload_base=0xE55B0000, fatal_err=0x60c048a8, usb_interrupt=0x60C02000, usb_getch=0x60c03f74, usb_send=0x60c04178, usb_send_commit=0x60c03af4,
        onenand_addr=0x30000000),

    ################################################################################################
    # MITSUBISHI
    ################################################################################################

    Device("d902i", 0x06d3, 0x20b0, {"dump_java": FujitsuJavaDumper()}),
    Device("d902is", 0x06d3, 0x2120, {"dump_java": FujitsuJavaDumper()}),
    Device("d702i", 0x06d3, 0x2100, {"dump_java": FujitsuJavaDumper()}),
    Device("d703i", 0x06d3, 0x2160, {"dump_java": FujitsuJavaDumper()}),
    Device("d903itv", 0x06d3, 0x2170, {"dump_java": FujitsuJavaDumper()}),
    Device("d904i", 0x06d3, 0x2190, {"dump_java": FujitsuJavaDumper()}),
    Device("d704i", 0x06d3, 0x21a0, {"dump_java": FujitsuJavaDumper()}),

    Device("d905i", 0x06d3, 0x21b0, {
        "dump_java": FujitsuJavaDumper(),
        "dump_nor": ShSrecExploitMemoryDumper(base=0x30000000, size=MB(128)),
        "nand_id": ShSrecExploitNandId(),
        "dump_nand": ShSrecExploitNandDumper(size=MB(256)),
    }, payload_base=0x64000000, fatal_err=0x64606890, usb_interrupt=0x64601000, usb_getch=0x6460380c, usb_send=0x64603a80, usb_send_commit=0x6460339c,
        nand_data=0x10000000, nand_addr=0x10000010, nand_cmd=0x10000020),

    Device("d705i", 0x06d3, 0x21d0, {"dump_java": FujitsuJavaDumper()}),
    Device("d705iu", 0x06d3, 0x21c0, {"dump_java": FujitsuJavaDumper()}),
]
