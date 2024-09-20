from dump.common.common_probe_onenand import CommonProbeOnenand
from dump.pipl.pipl_exploit import PiplExploit
from dump.nec.nec_pipl_rw_access import NecPiplRwAccess


class PiplProbeOnenand(CommonProbeOnenand, NecPiplRwAccess, PiplExploit):
    pass
