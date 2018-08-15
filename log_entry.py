
import datetime

class LogEntry:
    def __init__(self, log_line=None):
        if not log_line:
            self.timestamp = datetime.datetime(1971,1,1,0,0,0)
            self.driver = ''
            self.isMember = False
            self.date = datetime.date(1971,1,1)
            self.meter = 0
            self.renter = ''
            self.isStarting = False
            self.email = ''
            self.usingTowbar = False
            return

        # Get time
        date_and_time = log_line[0].split()
        date = date_and_time[0].split('-')
        time = date_and_time[1].split('.')
        self.timestamp = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]))

        # Get driver name
        self.driver = log_line[1]

        # Get if the driver/renter is a member of Y-sektionen
        self.isMember = log_line[2] in ['ja', 'JA', 'Ja']

        # Get date of drive
        date = log_line[3].split('-')
        self.date = datetime.date(int(date[0]), int(date[1]), int(date[2]))

        # Get meter
        self.meter = int(log_line[4])

        # Get renter
        self.renter = log_line[5]

        # Get starting or ending
        self.isStarting = log_line[6] in ['påbörjats', 'PÅBÖRJATS', 'Påbörjats']

        # Get email
        self.email = log_line[7]

        # Get if towbar used
        self.usingTowbar = log_line[8] in ['ja', 'JA', 'Ja']

    def copyValues(self, other):
        self.timestamp = other.timestamp
        self.driver = other.driver
        self.isMember = other.isMember
        self.date = other.date
        self.meter = other.meter
        self.renter = other.renter
        self.isStarting = other.isStarting
        self.email = other.email
        self.usingTowbar = other.usingTowbar

    def printEntry(self):
        print("Timestamp:\t", self.timestamp)
        print("Driver:\t\t", self.driver)
        print("Member:\t\t", self.isMember)
        print("Date:\t\t", self.date)
        print("Meter:\t\t", self.meter)
        print("Renter:\t\t", self.renter)
        print("Starting:\t", self.isStarting)
        print("Email:\t\t", self.email)
        print("Using towbar:\t", self.usingTowbar)

    def dateInInterval(self, from_date, until_date):
        if from_date:
            if self.date < from_date:
                # Before from_date
                return False
        if until_date:
            if self.date > until_date:
                # After until_date
                return False
        return True