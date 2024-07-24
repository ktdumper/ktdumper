from dump.common_onenand_dumper import CommonOnenandDumper
from dump.common_rw_access import CommonRwAccess
from dump.pipl_exploit import PiplExploit


class PiplOnenandDumper(CommonOnenandDumper, CommonRwAccess, PiplExploit):
    pass
