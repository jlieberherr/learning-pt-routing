class ConnectionScanData:
    def __init__(self, stops_per_id, footpaths_per_from_to_stop_id, trips_per_id):
        self.stops_per_id = stops_per_id
        self.footpaths_per_from_to_stop_id = footpaths_per_from_to_stop_id
        # TODO create sorted connection array from trips

class ConnectionScanCore:
    def __init__(self, connection_scan_data):
        self.connection_scan_data = connection_scan_data
    
    def route(from_stop_id, to_stop_id, desired_dep_time):
        return None # TODO