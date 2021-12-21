import re
from typing import Optional, List

from common import CourtInfo

court_info_raw: Optional[str] = "Фрунзенский районный суд г. Иваново, 153003, г. Иваново, ул. Мархлевского, д. 33"
court_info_agg: List[str] = re.split(",?\\s*\\d{6}\\s*,?", court_info_raw)
post_code = re.findall("\\d{6}", court_info_raw)
if len(court_info_agg) == 2 and len(post_code) == 1:
    address: str = f"{post_code[0]}, {court_info_agg[1]}"
    chosen_court: CourtInfo = CourtInfo(name=court_info_agg[0], address=address, note="")
    print(chosen_court)