class Stop:
    def __init__(self, id, code, name, easting, northing):
        self.id = id
        self.code = code
        self.name = name
        self.easting = easting
        self.northing = northing

class Footpath:
    def __init__(self, from_stop_id, to_stop_id, walking_time):
        self.from_stop_id = from_stop_id
        self.to_stop_id = to_stop_id
        self.walking_time = walking_time

class Connection:
    def __init__(self, from_stop_id, to_stop_id, dep_time, arr_time):
        self.from_stop_id = from_stop_id
        self.to_stop_id = to_stop_id
        self.dep_time = dep_time
        self.arr_time = arr_time



