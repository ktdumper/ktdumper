from dump.common_onenand_id import CommonOnenandId
from dump.pipl.pipl_exploit import PiplExploit
from dump.nec.nec_pipl_rw_access import NecPiplRwAccess


class PiplOnenandId(CommonOnenandId, NecPiplRwAccess, PiplExploit):
    pass
