class Stop:
    def __init__(self, id, code, name, easting, northing):
        self.id = id
        self.code = code
        self.name = name
        self.easting = easting
        self.northing = northing

    def __str__(self):
        return "[id={}, code={}, name={}]".format(self.id, self.code, self.name)
    
    def __repr__(self):
        return str(self)

class Footpath:
    def __init__(self, from_stop_id, to_stop_id, walking_time):
        self.from_stop_id = from_stop_id
        self.to_stop_id = to_stop_id
        self.walking_time = walking_time

    def __str__(self):
        return "[from_stop_id={}, to_stop_id={}, walking_time={}]".format(self.from_stop_id, self.to_stop_id, self.walking_time)
    
    def __repr__(self):
        return str(self)

class Connection:
    def __init__(self, trip_id, from_stop_id, to_stop_id, dep_time, arr_time):
        if dep_time > arr_time:
            raise ValueError("dep_time ({}) <= arr_time {} does not hold".format(dep_time, arr_time))
        self.trip_id = trip_id
        self.from_stop_id = from_stop_id
        self.to_stop_id = to_stop_id
        self.dep_time = dep_time
        self.arr_time = arr_time

    def __str__(self):
        return "[trip_id={}, from_stop_id={}, to_stop_id={}, dep_time={}, arr_time={}]".format(
            self.trip_id, 
            self.from_stop_id, 
            self.to_stop_id, 
            self.dep_time, 
            self.arr_time)
    
    def __repr__(self):
        return str(self)

class Trip:
    def __init__(self, id, connections):
        self.id = id
        for i in range(len(connections) - 1):
            act_con = connections[i]
            next_con = connections[i + 1]
            if act_con.to_stop_id != next_con.from_stop_id:
                raise ValueError("to_stop_id of connection {} does not equal from_stop_id of next connection {}".format(act_con, next_con))
            if act_con.arr_time > next_con.dep_time:
                raise ValueError("arr_time of connection {} is > than dep_time of next connection {}".format(act_con, next_con))
        self.connections = connections
        
    def __str__(self):
        return "[id={}, first_stop_id={}, last_stop_id={}, dep_in_first_stop={}, arr_in_last_stop={}, #connections={}]".format(
            self.id, 
            self.connections[0].from_stop_id if self.connections else "",
            self.connections[-1].to_stop_id if self.connections else "",
            self.connections[0].dep_time if self.connections else "",
            self.connections[-1].arr_time if self.connections else "",
            len(self.connections))
    
    def __repr__(self):
        return str(self)

    def get_all_from_stop_ids(self):
        return [c.from_stop_id for c in self.connections]
    
    def get_all_to_stop_ids(self):
        return [c.to_stop_id for c in self.connections]
    
    def get_set_of_all_stop_ids(self):
        return set(self.get_all_from_stop_ids()).union(set(self.get_all_to_stop_ids()))




