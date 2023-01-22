from typing import List, Optional
from datetime import datetime
from enum import Enum, IntEnum

from pydantic import BaseModel, constr

class OwntracksBatteryStatus(IntEnum):
    unknown = 0
    unplugged = 1
    charging = 2
    charged = 3

class OwntracksTrigger(str, Enum):
    bg_task_ping = 'p'
    circular_region = 'c'
    beacon = 'b'
    response_to_cmd = 'r'
    manual = 'u'
    timer_based_in_move = 't'
    updated_by_ios = 'v'

class OwntracksConnection(str, Enum):
    wifi = 'w'
    offline = 'o'
    mobile = 'm'
    unknown = 'u'

class OwntracksEventType(str, Enum):
    location = 'location'
    cmd = 'cmd'
    card = 'card'
    transition = 'transition'

class OwntracksEncryptedType(str, Enum):
    encrypted = 'encrypted'

class OwntracksEncryptedRecordBase(BaseModel):
    _type: OwntracksEncryptedType
    data: bytes

class OwntracksRecordBase(BaseModel):
    _type: OwntracksEventType
    BSSID: Optional[str] = None
    SSID: Optional[str] = None
    acc: Optional[float] = None
    alt: Optional[float] = None
    lon: float
    lat: float
    batt: Optional[float] = None
    bs: Optional[OwntracksBatteryStatus] = OwntracksBatteryStatus.unknown
    conn: Optional[OwntracksConnection] = OwntracksConnection.unknown
    tid: constr(min_length=2, max_length=2)
    created_at: Optional[int] = 0
    inregions: Optional[List[str]] = None
    t: Optional[OwntracksTrigger] = None
    topic: str
    tst: int
    vac: Optional[float] = None
    vel: Optional[float] = None