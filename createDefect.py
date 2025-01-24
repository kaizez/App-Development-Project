class BikeDefect:
    count_id = 0

    def __init__(self, bike_id, defect_type, date_found, bike_location, severity, description):
        BikeDefect.count_id += 1
        self.__bike_id = bike_id
        self.__defect_type = defect_type
        self.__date_found = date_found
        self.__bike_location = bike_location
        self.__severity = severity
        self.__description = description
        self.__status = "Pending"  # Default status
        self.__report_id = BikeDefect.count_id

    # Add new getters
    def get_status(self):
        return self.__status

    def get_report_id(self):
        return self.__report_id

    # Add status setter
    def set_status(self, status):
        self.__status = status

    # Existing getters/setters remain the same
    def get_bike_id(self):
        return self.__bike_id

    def get_defect_type(self):
        return self.__defect_type

    def get_date_found(self):
        return self.__date_found

    def get_bike_location(self):
        return self.__bike_location

    def get_severity(self):
        return self.__severity

    def get_description(self):
        return self.__description