class Station:
    def __init__(self, pk, name, lat, lng):
        self.pk = pk
        self.name = name
        self.lat = lat
        self.lng = lng
        self._raw = None

    @property
    def type(self):
        if self._raw is None:
            return "unknown"
        if self.name.startswith("Public Rack - "):
            return "public"
        if self._raw.get("station_type") == "classic" or self._raw.get("isLightweight") == False:
            return "classic"
        if self._raw.get("isLightweight") or self._raw.get("station_type") == "lightweight":
            return "ebike"

    @property
    def loc(self):
        return self.lat, self.lng

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
        pre = self.type.capitalize() + " "
        if pre == "Classic ":
            pre = ""
        return f"<{pre}Station at ({self.lat}, {self.lng}): {self.name}>"
