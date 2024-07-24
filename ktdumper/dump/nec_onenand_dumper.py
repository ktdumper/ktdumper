from dump.common_onenand_dumper import CommonOnenandDumper
from dump.common_rw_access import CommonRwAccess
from dump.nec_protocol import NecProtocol


class NecOnenandDumper(CommonOnenandDumper, CommonRwAccess, NecProtocol):
    pass
