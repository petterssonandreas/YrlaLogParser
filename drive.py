
import datetime
from log_entry import LogEntry

class Drive:
    def __init__(self, start_log_entry, end_log_entry):
        self.renter = start_log_entry.renter
        self.driver = start_log_entry.driver
        self.date = start_log_entry.date
        self.distance = end_log_entry.meter - start_log_entry.meter
        self.email = start_log_entry.email
        self.isMember = (start_log_entry.isMember or end_log_entry.isMember)
        self.usingTowbar = (start_log_entry.usingTowbar or end_log_entry.usingTowbar)

    def printDrive(self):
        print("Renter:\t\t", self.renter)
        print("Driver:\t\t", self.driver)
        print("Date:\t\t", self.date)
        print("Distance:\t", self.distance)
        print("Email:\t\t", self.email)
        print("Member:\t\t", self.isMember)
        print("Using towbar:\t", self.usingTowbar)
