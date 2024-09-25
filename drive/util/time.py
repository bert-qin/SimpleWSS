import datetime


def get_iso_str_time(time_delta_sec: int = None):
    time = datetime.datetime.utcnow()
    if time_delta_sec:
        time = time + datetime.timedelta(seconds=time_delta_sec)
    return time.isoformat(timespec='seconds')+'Z'

def get_yyyy_mm_dd_hh_mm_ss(date_time: datetime.datetime = None):
    if date_time == None:
        date_time = datetime.datetime.now()
    return date_time.strftime("%Y-%m-%d %H:%M:%S")