import logging

import urllib3

from divvybikes.models import Station
from divvybikes.util import filesystem_cache


log = logging.getLogger(__name__)
STATION_INFO_URI = "https://gbfs.divvybikes.com/gbfs/en/station_information.json"


@filesystem_cache(fname="/tmp/station-info.json")
def _fetch_stations_raw():
    resp = urllib3.request("GET", STATION_INFO_URI)
    data = resp.json()
    log.debug("fetched %s stations", len(data["data"]["stations"]))
    return data


def get_stations():
    stations = _fetch_stations_raw()["data"]["stations"]
    result = [Station.fromraw(x) for x in stations]
    return result


def get_public_rack_locations():
    stations = get_stations()
    locations_by_type = {k: set() for k in ("public", "classic", "ebike")}
    for station in stations:
        locations_by_type[station.type].add(station.loc)
    racks = locations_by_type["public"]
    # if a Public Rack is coincident with a real station, don't want to filter that location out
    racks -= locations_by_type["ebike"]
    racks -= locations_by_type["classic"]
    return racks
