from dump.common_onenand_id import CommonOnenandId
from dump.pipl_exploit import PiplExploit
from dump.common_rw_access import CommonRwAccess


class PiplOnenandId(CommonOnenandId, CommonRwAccess, PiplExploit):
    pass
