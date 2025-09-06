import logging
from pathlib import Path

import urllib3

from divvybikes.util import filesystem_cache


log = logging.getLogger(__name__)
AUTH_TOKEN_PATH = Path("~/.lyft_token").expanduser()
URI = "https://api.lyft.com/v1/last-mile/city-explorer-map-items"


def _get_token():
    if not AUTH_TOKEN_PATH.exists():
        raise Exception(
            "You need to have a valid Lyft auth token to access the City Explorer API endpoint.\n"
            f"Get this from browser cookies and place it in a text file at {AUTH_TOKEN_PATH}"
        )
    return AUTH_TOKEN_PATH.read_text().split()[0]


@filesystem_cache(fname="/tmp/city-explorer-map-items.json")
def _get_city_explorer_map_items_raw(token=None):
    if token is None:
        token = _get_token()
    headers = {
        "User-Agent": "com.motivateco.chicagoapp:iOS:15.7:14.47.3.169427500",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
    }
    resp = urllib3.request("POST", URI, headers=headers, timeout=30)
    if resp.status == 401:
        raise Exception("dead token")
    results = resp.json()
    log.debug("fetched %d city explorer map items", len(results["map_items"]))
    return results


def get_city_explorer_map_items(token=None, dedupe=True):
    raw_items = _get_city_explorer_map_items_raw(token)["map_items"]
    visited = [x for x in raw_items if "icon" in x["single_icon_bubble"]]
    unvisited = [x for x in raw_items if "icon" not in x["single_icon_bubble"]]
    locs_visited = {(x["location"]["lat"], x["location"]["lng"]) for x in visited}
    locs_unvisited = {(x["location"]["lat"], x["location"]["lng"]) for x in unvisited}
    intersection = locs_visited & locs_unvisited
    if dedupe and intersection:
        # how can a location be both unvisited and visited?
        # perhaps when there are coincident stations at a lat/lng
        log.debug("pruned %d invalid items %s from unvisited", len(intersection), intersection)
        locs_unvisited -= intersection
    return locs_visited, locs_unvisited
