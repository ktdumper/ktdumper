from dump.common_onenand_dumper import CommonOnenandDumper
from dump.nec.nec_pipl_rw_access import NecPiplRwAccess
from dump.pipl.pipl_exploit import PiplExploit


class PiplOnenandDumper(CommonOnenandDumper, NecPiplRwAccess, PiplExploit):
    pass
