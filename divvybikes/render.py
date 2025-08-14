import argparse
import logging
import webbrowser
from collections import defaultdict
from pathlib import Path

import gmplot

from divvybikes.explorer import get_city_explorer_map_items
from divvybikes.inventory import get_public_rack_locations
from divvybikes.inventory import get_stations
from divvybikes.maps import get_google_api_key
from divvybikes.maps import truncate_loc


log = logging.getLogger(__name__)


def city_explorer_main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="more verbose logging", action="store_true")
    args = parser.parse_args()
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)

    stations = get_stations()
    loc2name = defaultdict(list)
    loc2stations = defaultdict(list)

    counts = dict.fromkeys(["classic", "ebike", "public"], 0)
    visits = dict.fromkeys(["classic", "ebike", "public"], 0)
    for s in stations:
        loc2name[truncate_loc(s.loc)].append(s.name)
        loc2stations[truncate_loc(s.loc)].append(s)
        counts[s.type] += 1

    all_visited, all_unvisited = get_city_explorer_map_items()
    public_rack_locations = {truncate_loc(x) for x in get_public_rack_locations()}

    key = get_google_api_key()
    gmap = gmplot.GoogleMapPlotter(lat=41.897764, lng=-87.642884, zoom=12, apikey=key)

    for loc in all_unvisited:
        if loc in public_rack_locations:
            continue
        title = ", ".join(dict.fromkeys(loc2name[loc]))
        types = {x.type for x in loc2stations[loc]}
        label = None
        if types == {"classic"}:
            color = "grey"
        elif types == {"ebike"}:
            color = "orange"
            label = "⚡"
        else:
            color = "white"
            label = "2"
            # there is both a lightweight and a classic station at the same loc!
        gmap.marker(*loc, color=color, size=100, info_window=title, title=title, label=label)

    for loc in all_visited:
        types = {x.type for x in loc2stations[loc]}
        if loc in public_rack_locations:
            visits["public"] += 1
            continue
        label = "✓"
        if types == {"classic"}:
            visits["classic"] += 1
        elif types == {"ebike"}:
            label = "⚡"
            visits["ebike"] += 1
        else:
            log.warning("ambiguous visit at %s", loc)
        title = ", ".join(loc2name[loc])
        gmap.marker(*loc, color="green", size=100, info_window=title, title=title, label=label)

    n_visited = len(all_visited)
    log.info("%d Stations Visited", n_visited)
    log.info("That's %s of Divvy locations", f"{n_visited / len(stations):.1%}")
    log.info("%d/%d Classic stations visited", visits["classic"], counts["classic"])
    log.info("%d/%d Ebike stations visited", visits["ebike"], counts["ebike"])
    log.info("%d/%d Public racks visited", visits["public"], counts["public"])

    # no markers for the public racks, just small gray circles
    gmap.scatter(*zip(*public_rack_locations), color="gray", size=50, marker=False)

    path = Path(__file__).parent / "map.html"
    gmap.draw(path)
    log.info(f"wrote {path}")
    webbrowser.open(f"file:///{path}")


if __name__ == "__main__":
    city_explorer_main()
