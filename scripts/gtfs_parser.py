import csv
from datetime import date
from io import TextIOWrapper
from zipfile import ZipFile

from scripts.classes import Footpath, Stop
from scripts.connectionscan_router import ConnectionScanData

def get_index_with_default(header, column_name, default_value=None):
    return header.index(column_name) if column_name in header else default_value


def parse_yymmdd(yymmdd_str):
    y = int(yymmdd_str[:4])
    m = int(yymmdd_str[4:6])
    d = int(yymmdd_str[6:8])
    return date(y, m, d)
    

def parse_gtfs(path_to_gtfs_zip, desired_date):
    stops_per_id = {}
    footpaths_per_from_to_stop_id = {}

    with ZipFile(path_to_gtfs_zip, "r") as zip:

        with zip.open("stops.txt", "r") as gtfs_file:
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

        with zip.open("transfers.txt", "r") as gtfs_file:
            reader = csv.reader(TextIOWrapper(gtfs_file, "utf-8"))
            header = next(reader)
            from_stop_id_index = header.index("from_stop_id") # required
            to_stop_id_index = header.index("to_stop_id") # required
            transfer_type_index = header.index("transfer_type") # required
            min_transfer_time_index = get_index_with_default(header, "min_transfer_time") # optional
            if min_transfer_time_index:
                for row in reader:
                    if row[transfer_type_index] == "2":
                        from_stop_id = row[from_stop_id_index]
                        to_stop_id = row[to_stop_id_index]
                        footpaths_per_from_to_stop_id[(from_stop_id, to_stop_id)] = Footpath(
                            from_stop_id, 
                            to_stop_id, 
                            int(row[min_transfer_time_index]))
            else:
                raise ValueError("min_transfer_time column in gtfs transfers.txt file is not definied, cannot calculate footpaths.")
        
        service_available_at_date_per_service_id = get_service_available_at_date_per_service_id(zip, desired_date)

    return ConnectionScanData(stops_per_id, footpaths_per_from_to_stop_id, {})


def get_service_available_at_date_per_service_id(zip, desired_date):
    service_available_at_date_per_service_id = {}
    with zip.open("calendar.txt", "r") as gtfs_file:
        weekday_columns = ["monday", "tuesday", "wednesday", "thursday" , "friday", "saturday", "sunday"]
        reader = csv.reader(TextIOWrapper(gtfs_file, "utf-8"))
        header = next(reader)
        service_id_index = header.index("service_id") # required
        weekday_index = header.index(weekday_columns[desired_date.weekday()]) # required
        start_date_index = header.index("start_date") # required
        end_date_index = header.index("end_date") # required
        for row in reader:
            start_date = parse_yymmdd(row[start_date_index])
            end_date = parse_yymmdd(row[end_date_index])
            service_available_at_date_per_service_id[row[service_id_index]] = True if start_date <= desired_date <= end_date and row[weekday_index] == "1" else False
    
    with zip.open("calendar_dates.txt", "r") as gtfs_file:
        reader = csv.reader(TextIOWrapper(gtfs_file, "utf-8"))
        header = next(reader)
        service_id_index = header.index("service_id") # required
        date_index = header.index("date") # required
        exception_type_index = header.index("exception_type") # required
        for row in reader:
            service_id = row[service_id_index]
            date_ = parse_yymmdd(row[date_index])
            if date_ == desired_date:
                exception_type = row[exception_type_index]
                if exception_type == "1":
                    service_available_at_date_per_service_id[service_id] = True
                elif exception_type == "2":
                    service_available_at_date_per_service_id[service_id] = False
                else:
                    raise ValueError("as exception_type only 1 or 2 are permitted, but is: {}".format(exception_type))
    return service_available_at_date_per_service_id

def get_trip_available_at_date_per_trip_id(zip, service_available_at_date_per_service_id):
    trip_available_at_date_per_trip_id = {}
    with zip.open("trips.txt", "r") as gtfs_file:
        reader = csv.reader(TextIOWrapper(gtfs_file, "utf-8"))
        header = next(reader)
        trip_id_index = header.index("trip_id") # required
        service_id_index = header.index("service_id") # required
        for row in reader:
            trip_available_at_date_per_trip_id[row[trip_id_index]] = service_available_at_date_per_service_id[row[service_id_index]]
    return trip_available_at_date_per_trip_id