#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple

from scripts.helpers.funs import seconds_to_hhmmss


class Stop:
    __slots__ = ["id", "code", "name", "easting", "northing"]
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
    __slots__ = ["from_stop_id", "to_stop_id", "walking_time"]
    def __init__(self, from_stop_id, to_stop_id, walking_time):
        self.from_stop_id = from_stop_id
        self.to_stop_id = to_stop_id
        self.walking_time = walking_time

    def __str__(self):
        return "[from_stop_id={}, to_stop_id={}, walking_time={}]".format(self.from_stop_id, self.to_stop_id, self.walking_time)
    
    def __repr__(self):
        return str(self)

class Connection:
    __slots__ = ["trip_id", "from_stop_id", "to_stop_id", "dep_time", "arr_time"]
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
            seconds_to_hhmmss(self.dep_time), 
            seconds_to_hhmmss(self.arr_time))
    
    def __repr__(self):
        return str(self)

class JourneyLeg:
    __slots__ = ["in_connection", "out_connection", "footpath"]
    def __init__(self, in_connection, out_connection, footpath):
        if in_connection.trip_id != out_connection.trip_id:
            raise ValueError("trip_id {} of in_connection is not equal to trip_id {} of out_connection.".format(in_connection.trip_id, out_connection.trip_id))
        if in_connection != out_connection:
            if in_connection.arr_time > out_connection.dep_time:
                raise ValueError("arr_time {} of in_connection is after dep_time {} of out_connection.".format(seconds_to_hhmmss(in_connection.arr_time), seconds_to_hhmmss(out_connection.dep_time)))
        if footpath is not None:
            if out_connection.to_stop_id != footpath.from_stop_id:
                raise ValueError("to_stop_id {} of out_connection is not equal to from_stop_id {} of footpath".format(out_connection.to_stop_id, footpath.from_stop_id))
        self.in_connection = in_connection
        self.out_connection = out_connection
        self.footpath = footpath
    
    def get_trip_id(self):
        return self.in_connection.trip_id
    
    def get_in_stop_id(self):
        return self.in_connection.from_stop_id
    
    def get_out_stop_id(self):
        return self.out_connection.to_stop_id
    
    def get_dep_time_in_stop_id(self):
        return self.in_connection.dep_time
    
    def get_arr_time_out_stop_id(self):
        return self.out_connection.arr_time
    
    def __str__(self):
        return "[trip_id={}, in_stop_id={}, out_stop_id={}, dep_time={}, arr_time={}]".format(
            self.get_trip_id(), 
            self.get_in_stop_id(),
            self.get_out_stop_id(),
            seconds_to_hhmmss(self.get_dep_time_in_stop_id()),
            seconds_to_hhmmss(self.get_arr_time_out_stop_id())
            )
    
    def __repr__(self):
        return str(self)

class Journey:
    __slots__ = ["journey_legs"]
    # TODO test this class
    def __init__(self):
        self.journey_legs = []
    
    def prepend_journey_leg(self, journey_leg):
        self.journey_legs = [journey_leg] + self.journey_legs
    
    def get_nb_journey_legs(self):
        return len(self.journey_legs)
    
    def get_nb_pt_journey_legs(self):
        return len([leg for leg in self.journey_legs if leg.in_connection is not None])
    
    def has_legs(self):
        return len(self.journey_legs) > 0

    def is_first_leg_footpath(self):
        if self.has_legs():
            return True if self.journey_legs[0].in_connection is None else False
        else:
            return False
    
    def is_last_leg_footpath(self):
        if self.has_legs():
            return True if self.journey_legs[-1].footpath is not None else False
        else:
            return False
    
    def get_first_stop_id(self):
        if self.has_legs():
            first_journey_leg = self.journey_legs[0]
            if self.is_first_leg_footpath():
                return first_journey_leg.footpath.from_stop_id
            else:
                return first_journey_leg.in_connection.from_stop_id
        else:
            return None
    
    def get_last_stop_id(self):
        if self.has_legs() > 0:
            last_journey_leg = self.journey_legs[-1]
            if self.is_last_leg_footpath():
                return last_journey_leg.footpath.to_stop_id
            else:
                return last_journey_leg.out_connection.to_stop_id
        else:
            return None

class Trip:
    __slots__ = ["id", "connections"]
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
            seconds_to_hhmmss(self.connections[0].dep_time) if self.connections else "",
            seconds_to_hhmmss(self.connections[-1].arr_time) if self.connections else "",
            len(self.connections))
    
    def __repr__(self):
        return str(self)

    def get_all_from_stop_ids(self):
        return [c.from_stop_id for c in self.connections]
    
    def get_all_to_stop_ids(self):
        return [c.to_stop_id for c in self.connections]
    
    def get_set_of_all_stop_ids(self):
        return set(self.get_all_from_stop_ids()).union(set(self.get_all_to_stop_ids()))
