from dump.v2.onenand_fast_v2 import OnenandFast_v2
from dump.v2.rw_access_v2 import RwAccess_v2
from dump.pipl.pipl_exploit_v2 import PiplExploit_v2


class PiplOnenandFast_v2(OnenandFast_v2, RwAccess_v2, PiplExploit_v2):
    pass
