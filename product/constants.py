from enum import IntEnum


class Stream(IntEnum):
    STARTED = 0
    CSV_LIST = 1
    BULK_CREATE = 2
    STREAM_LIMIT = 4
