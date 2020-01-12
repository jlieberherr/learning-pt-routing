import csv
from io import TextIOWrapper
from zipfile import ZipFile

from scripts.classes import Stop, Footpath
from scripts.connectionscan_router import ConnectionScanData


def get_index_with_default(header, column_name, default_value=None):
    return header.index(column_name) if column_name in header else default_value
    

def parse_gtfs(path_to_gtfs_zip):
    stops_per_id = {}
    footpaths_per_from_to_stop_id = {}
    with ZipFile(path_to_gtfs_zip, "r") as zip:
        for name in zip.namelist():
            if name == "stops.txt":
                with zip.open(name, "r") as gtfs_file:
                    reader = csv.reader(TextIOWrapper(gtfs_file, "utf-8"))
                    header = next(reader)
                    id_index = header.index("stop_id") # required
                    code_index = get_index_with_default(header, "stop_code") # optional
                    name_index = get_index_with_default(header, "stop_name") # conditionally required
                    lat_index = get_index_with_default(header, "stop_lat") # conditionally required
                    lon_index = get_index_with_default(header, "stop_lon") # conditionally required
                    for row in reader:
                        stop_id = row[id_index]
                        stops_per_id[stop_id] = Stop(
                            stop_id, 
                            row[code_index] if code_index else "", 
                            row[name_index] if name_index else "", 
                            float(row[lon_index]) if lon_index else 0.0,
                            float(row[lat_index]) if lat_index else 0.0,
                            )
            elif name == "transfers.txt":
                with zip.open(name, "r") as gtfs_file:
                    reader = csv.reader(TextIOWrapper(gtfs_file, "utf-8"))
                    header = next(reader)
                    from_stop_id_index = header.index("from_stop_id") # required
                    to_stop_id_index = header.index("to_stop_id") # required
                    transfer_type_index = header.index("transfer_type") # required
                    min_transfer_time = header.index("min_transfer_time") # optional
                    for row in reader:
                        if row[transfer_type_index] == "2":
                            from_stop_id = row[from_stop_id_index]
                            to_stop_id = row[to_stop_id_index]
                            footpaths_per_from_to_stop_id[(from_stop_id, to_stop_id)] = Footpath(from_stop_id, to_stop_id, int(row[min_transfer_time]))

    return ConnectionScanData(stops_per_id, footpaths_per_from_to_stop_id, {})