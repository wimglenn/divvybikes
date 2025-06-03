import logging
import math
import os
from functools import cache
from pathlib import Path


log = logging.getLogger(__name__)


def get_google_api_key():
    key_path = Path("~/.google_api_key").expanduser()
    if key_path.is_file():
        key = key_path.read_text().strip()
    else:
        key = os.environ.get("GOOGLE_API_KEY", "")
    if not key:
        # maps don't render as nicely without auth key
        log.warning("unset $GOOGLE_API_KEY")
    return key


@cache
def haversine(lat1, lng1, lat2, lng2):
    # approximate distance in meters between two lat/lng coords
    lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
    dlng = lng2 - lng1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6_378_137  # radius of earth at sea level in meters
    r += 176.5  # elevation of Chicago above sea level
    return c * r


def truncate(f, n):
    """Truncates/pads a float f to n decimal places without rounding"""
    i, d = str(f).split(".")
    return float(i + "." + d[:n])


def truncate_loc(loc):
    # city explorer map lat/lng have only 6 digits after the decimal place,
    # but the station-info feed has more accurate locations
    lat, lng = loc
    return truncate(lat, 6), truncate(lng, 6)
