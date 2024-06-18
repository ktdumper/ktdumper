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


def MB(x):
    return x*1024*1024


DEVICES = [
    ################################################################################################
    # CASIO
    ################################################################################################

    # 830CA
    # PARTIAL - NOR dump only
    Device("830ca", 0x1967, 0x2002, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee50dc, usb_data= 0x33ef5126, usb_datasz=0x33ef5120, usb_respfunc=0x5910,
       quirks=SLOW_READ),
    
    # 930CA
    Device("930ca", 0x1967, 0x2004, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee51a8, usb_data=0x33ef51f2, usb_datasz=0x33ef51ec, usb_respfunc=0x50a8,
       quirks=SLOW_READ),
    
    ################################################################################################
    # NEC
    ################################################################################################
    
    #DOCOMO

    # N900i
    Device("n900i", 0x0409, 0x0112, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(32)),
        "dump_nand": NecNandDumper(size=MB(32), quirks=SLOW_READ),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400),
    
    # N900iS
    Device("n900is", 0x0409, 0x0121, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(32), quirks=SLOW_READ),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400),
    
    # N901iC
    Device("n901ic", 0x0409, 0x0129, {
        "dump_nor": NecMemoryDumper(base=0x04000000, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(64), quirks=SLOW_READ, big=1),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400),
    
    # N901iS
    Device("n901is", 0x0409, 0x0144, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(64), quirks=SLOW_READ),
    }, payload_base=0x10000000, onenand_addr=0x06000000),

    # N701i
    Device("n701i", 0x0409, 0x0142, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(64), quirks=SLOW_READ),
    }, payload_base=0x10000000, onenand_addr=0x06000000),

    # N902i
    # NOR dump only
    Device("n902i", 0x0409, 0x014c, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x10000000, quirks=SLOW_READ),

    # N702iD
    Device("n702id", 0x0409, 0x0168, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(64), quirks=SLOW_READ),
    }, payload_base=0x10000000, onenand_addr=0x06000000),

    # N904i
    Device("n904i", 0x0409, 0x0200, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x08000000, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x06000000, quirks=SLOW_READ),

    # N905i
    Device("n905i", 0x0409, 0x0210, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33eec3f8, usb_data=0x33efc442, usb_datasz=0x33efc43c, usb_respfunc=0x4f58,
       quirks=SLOW_READ),

    # N905imyu
    Device("n905imyu", 0x0409, 0x0220, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33eec400, usb_data=0x33efc44a, usb_datasz=0x33efc444, usb_respfunc=0x4f94,
       quirks=SLOW_READ),
    
    # N706i
    # PARTIAL - NOR dump only
    Device("n706i", 0x0409, 0x023c, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee50d0, usb_data=0x33ef511a, usb_datasz=0x33ef5114, usb_respfunc=0x582c,
       quirks=SLOW_READ),

    # N706ie
    # PARTIAL- NOR dump only
    Device("n706ie", 0x0409, 0x024a, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x00000000, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee50d0, usb_data=0x33ef511a, usb_datasz=0x33ef5114, usb_respfunc=0x582c,
       quirks=SLOW_READ),
    
    # N706iII
    Device("n706i2", 0x0409, 0x0224, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee50d0, usb_data=0x33ef511a, usb_datasz=0x33ef5114, usb_respfunc=0x5520,
       quirks=SLOW_READ),
   
    
    # N-01A
    Device("n-01a", 0x0409, 0x0240, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5198, usb_data=0x33ef51e2, usb_datasz=0x33ef51dc, usb_respfunc=0x5098,
       quirks=SLOW_READ),

    # N-02A
    Device("n-02a", 0x0409, 0x025c, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nor_slow": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
        "nand_id": NecNandId(),
        "dump_nand_slow": NecNandDumperLpViaPoke(),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5198, usb_data=0x33ef51e2, usb_datasz=0x33ef51dc, usb_respfunc=0x519c,
       quirks=SLOW_READ),
       
    # N-03A
    Device("n-03a", 0x0409, 0x0268, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee50d0, usb_data=0x33ef511a, usb_datasz=0x33ef5114, usb_respfunc=0x582c,
       quirks=SLOW_READ),

    # N-04A
    Device("n-04a", 0x0409, 0x0260, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5198, usb_data=0x33ef51e2, usb_datasz=0x33ef51dc, usb_respfunc=0x50a8,
       quirks=SLOW_READ),

    # N-06A
    Device("n-06a", 0x0409, 0x0274, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5198, usb_data=0x33ef51e2, usb_datasz=0x33ef51dc, usb_respfunc=0x50e8,
       quirks=SLOW_READ),
          
    # N-07A
    Device("n-07a", 0x0409, 0x0280, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5198, usb_data=0x33ef51e2, usb_datasz=0x33ef51dc, usb_respfunc=0x50f0,
       quirks=SLOW_READ),

    # N-08A
    Device("n-08a", 0x0409, 0x026c, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5198, usb_data=0x33ef51e2, usb_datasz=0x33ef51dc, usb_respfunc=0x50e8,
       quirks=SLOW_READ),
       
    # N-03B - 1/23/2010 - M2
    Device("n-03b", 0x0409, 0x02a0, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5198, usb_data=0x33ef51e2, usb_datasz=0x33ef51dc, usb_respfunc=0x50d8,
       quirks=SLOW_READ),

# SOFTBANK

    # 820N
    # PARTIAL - NOR dump only
    Device("820n", 0x0409, 0x0250, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nor_slow": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33eec3f8, usb_data=0x33efc442, usb_datasz=0x33efc43c, usb_respfunc=0x4f58,
       quirks=SLOW_READ),
       
    # 930N
     Device("930n", 0x0409, 0x027c, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee5190, usb_data=0x33ef51da, usb_datasz=0x33ef51d4, usb_respfunc=0x50d4,
       quirks=SLOW_READ),

    # 831N
    # PARTIAL - NOR dump only
    Device("831n", 0x0409, 0x0284, {
        "dump_nor": NecMemoryDumperPayload(base=0x0, size=MB(128)),
        "dump_nand": NecNandDumperLp(size=MB(512)),
    }, payload_base=0x30000000, nand_data=0x10000000, nand_cmd=0x10020000, nand_addr=0x10040000,
       usb_command=0x33ee50c4, usb_data=0x33ef510e, usb_datasz=0x33ef5108, usb_respfunc=0x57dc,
       quirks=SLOW_READ),
    
    ################################################################################################
    # PANASONIC
    ################################################################################################

    # DOCOMO

    # P900i
    Device("p900i", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(32)),
        "dump_nand": NecNandDumper(size=MB(32)),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),

    # P900iV
    Device("p900iv", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(32)),
        "dump_nand": NecNandDumper(size=MB(32)),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),
    
    # P700i
    Device("p700i", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x0C000000, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(64), big=1),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),
    
    # P901i
    Device("p901i", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x0C000000, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(64), big=1),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),
   
    
    # P901iS
    Device("p901is", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x0C000000, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(64), big=1),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),
    
    
    # P901iTV
    Device("p901itv", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x90000000, onenand_addr=0x08000000, quirks=SLOW_READ),

    # P851i
    Device("p851i", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(64)),
        "dump_nand": NecNandDumper(size=MB(32), big=1),
    }, payload_base=0x10000000, nand_data=0x04000000, nand_cmd=0x04000800, nand_addr=0x04000400, quirks=SLOW_READ),

    # P902i
    Device("p902i", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x08000000, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x10000000, quirks=SLOW_READ),
    
    # P902iS
    Device("p902is", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x08000000, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x10000000, quirks=SLOW_READ),

    # P702i
    Device("p702i", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x08000000, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x10000000, quirks=SLOW_READ),

    # P702iD
    Device("p702id", 0x0a3c, 0x000d, {
        "dump_rom": NecMemoryDumper(base=0x0, size=0x8000),
        "dump_nor": NecMemoryDumper(base=0x08000000, size=MB(64)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x80000000, onenand_addr=0x10000000, quirks=SLOW_READ),

    # P903i
    Device("p903i", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x90000000, onenand_addr=0x08000000),

    # P903iTV
    Device("p903itv", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(256)),
    }, payload_base=0x90000000, onenand_addr=0x0C000000),

    # P904i
    Device("p904i", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(128)),
        "dump_nand": NecOnenandDumper(size=MB(512), has_ddp=True),
    }, payload_base=0x90040000, onenand_addr=0x0C000000),

    # P704i
    Device("p704i", 0x0a3c, 0x000d, {
        "dump_nor": NecMemoryDumper(base=0x0, size=MB(96)),
        "dump_nand": NecOnenandDumper(size=MB(128)),
    }, payload_base=0x90000000, onenand_addr=0x08000000),

    # P-01A
    Device("p-01a", 0x04da, 0x216b, {
        "dump_nor": PiplExploitMemoryDumper(base=0x0, size=MB(128)),
        "onenand_id": PiplOnenandId(),
        "dump_nand": PiplOnenandDumper(size=MB(512), has_ddp=True),
    }, exploit_flavor="A", payload_base=0x8009c000, onenand_addr=0x0C000000),

    # P-03A
    Device("p-03a", 0x04da, 0x216b, {
        "dump_nor": PiplExploitMemoryDumper(base=0x0, size=MB(128)),
        "onenand_id": PiplOnenandId(),
        "dump_nand": PiplOnenandDumper(size=MB(256)),
    }, exploit_flavor="A", payload_base=0x8009c000, onenand_addr=0x0C000000),

    # P-04A
    Device("p-04a", 0x04da, 0x216b, {
        "dump_nor": PiplExploitMemoryDumper(base=0x0, size=MB(128)),
        "onenand_id": PiplOnenandId(),
        "dump_nand": PiplOnenandDumper(size=MB(256)),
    }, exploit_flavor="A", payload_base=0x8009c000, onenand_addr=0x0C000000),

    
    # P-10A
    Device("p-10a", 0x04da, 0x216b, {
        "dump_nor": PiplExploitMemoryDumper(base=0x0, size=MB(128)),
        "onenand_id": PiplOnenandId(),
        "dump_nand": PiplOnenandDumper(size=MB(256)),
    }, exploit_flavor="A", payload_base=0x8009c000, onenand_addr=0x0C000000),

    # P-01B
    Device("p-01b", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand_a": PiplOnenandDumper(onenand_addr=0x0C000000, size=MB(512), has_ddp=True),
        "dump_nand_b": PiplOnenandDumper(onenand_addr=0x18000000, size=MB(256)),
    }, exploit_flavor="B", payload_base=0x83800000),

    # P-02B
    Device("p-02b", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "onenand_id_a": PiplOnenandId(onenand_addr=0x0C000000),
        "onenand_id_b": PiplOnenandId(onenand_addr=0x18000000),
        "dump_nand_a": PiplOnenandDumper(onenand_addr=0x0C000000, size=MB(512), has_ddp=True),
        "dump_nand_b": PiplOnenandDumper(onenand_addr=0x18000000, size=MB(256)),
    }, exploit_flavor="B", payload_base=0x83800000),

    # P-03B
    Device("p-03b", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand": PiplOnenandDumper(size=MB(512), has_ddp=True),
    }, exploit_flavor="B", payload_base=0x83800000, onenand_addr=0x0C000000),

    # P-04B
    Device("p-04b", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand_a": PiplOnenandDumper(onenand_addr=0x0C000000, size=MB(512), has_ddp=True),
        "dump_nand_b": PiplOnenandDumper(onenand_addr=0x18000000, size=MB(256)),
    }, exploit_flavor="B", payload_base=0x83800000),

    # P-07B
    Device("p-07b", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand": PiplOnenandDumper(size=MB(512)),
        "onenand_id": PiplOnenandId(),
    }, exploit_flavor="B", payload_base=0x83800000, onenand_addr=0x0C000000),

    # P-06C
    Device("p-06c", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand_peek_poke": PiplOnenandDumper(has_4k_pages=True, size=MB(1024)),
        "dump_nand": PiplOnenandFast(size=MB(1024)),
        "onenand_id": PiplOnenandId(),
    }, exploit_flavor="C", payload_base=0x83800000, onenand_addr=0x0C000000,
       usb_command=0x8115a960, usb_data=0x8115a54a, usb_datasz=0x8115a544, usb_respfunc=0x80027f6c),

    # P-01F
    Device("p-01f", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_emmc": PiplEmmcDumper(size=MB(2048)),
        "fuse_user": PiplEmmcFuse(offset=0x1a800000, size=0x3fe00000),
    }, exploit_flavor="C", payload_base=0x83800000, emmc_read_and_dcache=0x8000dba8, emmc_inv_dcache_and_write=0x8000dc80,
       usb_command=0x8115a960, usb_data=0x8115a54a, usb_datasz=0x8115a544, usb_respfunc=0x80010a1c),

    # P-01G
    Device("p-01g", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_emmc": PiplEmmcDumper(size=MB(2048)),
    }, exploit_flavor="C", payload_base=0x83800000, emmc_read_and_dcache=0x8000dbf4,
       usb_command=0x8115a960, usb_data=0x8115a54a, usb_datasz=0x8115a544, usb_respfunc=0x80010a68),

    # P-01H
    Device("p-01h", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_emmc": PiplEmmcDumper(size=MB(2048)),
    }, exploit_flavor="C", payload_base=0x83800000, emmc_read_and_dcache=0x8000dbf4,
       usb_command=0x8115a960, usb_data=0x8115a54a, usb_datasz=0x8115a544, usb_respfunc=0x80010a68),
       
    # SOFTBANK
    
    # 930P
    Device('930p', 0x04da, 0x216b, {
        'dump_rom': PiplExploitMemoryDumper(base=0x0, size=0x8000),
        'dump_nand': PiplOnenandDumper(onenand_addr=0x0C000000, size=MB(512), has_ddp=True),
    }, exploit_flavor="A", payload_base=0x8009c000),  
    
    # 940P
    Device("940p", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand_a": PiplOnenandDumper(onenand_addr=0x0C000000, size=MB(512), has_ddp=True),
        "dump_nand_b": PiplOnenandDumper(onenand_addr=0x18000000, size=MB(256)),
    }, exploit_flavor="B", payload_base=0x83800000),
    
    # 942P
    Device("942p", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x0, size=0x8000),
        "dump_nand_a": PiplOnenandDumper(onenand_addr=0x0C000000, size=MB(512), has_ddp=True),
        "dump_nand_b": PiplOnenandDumper(onenand_addr=0x18000000, size=MB(256)),
    }, exploit_flavor="B", payload_base=0x83800000),
  
    # 301P
    Device("301p", 0x04da, 0x216b, {
        "dump_rom": PiplExploitMemoryDumper(base=0x00000000, size=0x8000),
        "dump_emmc": PiplEmmcDumper(size=MB(2048)),
    }, exploit_flavor="C", payload_base=0x83800000, emmc_read_and_dcache=0x8000c528,
       usb_command=0x8115a960, usb_data=0x8115a54a, usb_datasz=0x8115a544, usb_respfunc=0x8000f39c),

    ################################################################################################
    # SHARP
    ################################################################################################
    
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
    Device("f905i", 0x04c5, 0x1128, {"dump_java": FujitsuJavaDumper()}),
    Device("f906i", 0x04c5, 0x115d, {"dump_java": FujitsuJavaDumper()}),
    Device("f-04a", 0x04c5, 0x115e, {"dump_java": FujitsuJavaDumper()}),
    Device("f-05a", 0x04c5, 0x1167, {"dump_java": FujitsuJavaDumper()}), 
    Device("f-07a", 0x04c5, 0x115f, {"dump_java": FujitsuJavaDumper()}), 
    Device("f-10a", 0x04c5, 0x1162, {"dump_java": FujitsuJavaDumper()}),
    
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
    Device("d905i", 0x06d3, 0x21b0, {"dump_java": FujitsuJavaDumper()}),
    Device("d705i", 0x06d3, 0x21d0, {"dump_java": FujitsuJavaDumper()}),
    Device("d705iu", 0x06d3, 0x21c0, {"dump_java": FujitsuJavaDumper()}),
]
