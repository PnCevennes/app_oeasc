from datetime import datetime

cur_time = ""


def checktime(s=""):
    global cur_time
    print(cur_time)
    if not cur_time:
        cur_time = datetime.now()
    else:
        print(s, (datetime.now() - cur_time).microseconds / 1e6)
        cur_time = datetime.now()
