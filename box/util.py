# -*- coding: utf-8 -*-


import datetime
import time


# Timezone-aware timestamp
def now():
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    timestamp = datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset))
    return timestamp
