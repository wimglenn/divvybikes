from .util import hyperlink


class Station:
    def __init__(self, pk, name, lat, lng):
        self.pk = pk
        self.name = name
        self.lat = lat
        self.lng = lng
        self._raw = {}

    @property
    def type(self):
        if self._raw.get("station_type") == "classic":
            return "Station"
        if "Public Rack" in self.name or self.name.endswith("Corral"):
            return "Rack"
        if self._raw.get("station_type") == "lightweight":
            # even though Lyft removed all "ebike-only" stations, there are
            # evidently still a couple of these left in db...
            return "Station"
        return "unknown"

    @property
    def loc(self):
        return self.lat, self.lng

    @property
    def link(self):
        url = f"https://www.google.com/maps/search/{self.lat},{self.lng}"
        return hyperlink(url)

    @classmethod
    def fromraw(cls, data):
        if "station_id" in data:
            # snake_case https://gbfs.divvybikes.com/gbfs/en/station_information.json
            pk = data["station_id"]
            name = data["name"]
            lat = data["lat"]
            lng = data["lon"]
        else:
            # camelCase https://account.divvybikes.com/bikesharefe-gql
            pk = data["stationId"]
            name = data["stationName"]
            lat = data["location"]["lat"]
            lng = data["location"]["lng"]
        obj = cls(pk, name, lat, lng)
        obj._raw = data
        return obj

    def __repr__(self):
        return f"<{self.type} at ({self.lat}, {self.lng}): {self.name}>"
