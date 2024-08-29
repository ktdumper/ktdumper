from dump.common_onenand_dumper import CommonOnenandDumper
from dump.nec_rw_access_v2 import NecRwAccess_v2
from dump.nec_protocol_v2 import NecProtocol_v2


class NecOnenandDumper_v2(CommonOnenandDumper, NecRwAccess_v2, NecProtocol_v2):
    pass
