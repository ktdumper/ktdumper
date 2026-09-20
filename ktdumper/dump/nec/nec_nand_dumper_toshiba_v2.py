from dump.nec.nec_protocol_v2 import NecProtocol_v2
from dump.v2.nand_dumper_toshiba_v2 import NandDumperToshiba_v2


class NecNandDumperToshiba_v2(NandDumperToshiba_v2, NecProtocol_v2):
    pass
