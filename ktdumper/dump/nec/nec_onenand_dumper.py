from dump.common_onenand_dumper import CommonOnenandDumper
from dump.nec.nec_pipl_rw_access import NecPiplRwAccess
from dump.nec.nec_protocol import NecProtocol


class NecOnenandDumper(CommonOnenandDumper, NecPiplRwAccess, NecProtocol):
    pass
