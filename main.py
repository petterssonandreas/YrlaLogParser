import datetime
import re
from log_entry import LogEntry
from drive import Drive
import webbrowser
import sys


'''
Interpret command line arguments, if present.
'''
from_date = None
until_date = None

if len(sys.argv) > 1:
    # Possible from-date
    data = str(sys.argv[1]).split('-')
    if len(data) == 3:
        # Assume date on form YYYY-MM-DD
        from_date = datetime.date(int(data[0]), int(data[1]), int(data[2]))
    elif len(data) == 1 and len(data[0]) == 6:
        # Assume 6 digits, YYMMDD
        from_date = datetime.date(int('20' + data[0][0:2]), int(data[0][2:4]), int(data[0][4:6]))

    if len(sys.argv) > 2:
        # Possible until-date
        data = str(sys.argv[2]).split('-')
        if len(data) == 3:
            # Assume date on form YYYY-MM-DD
            until_date = datetime.date(int(data[0]), int(data[1]), int(data[2]))
        elif len(data) == 1 and len(data[0]) == 6:
            # Assume 6 digits, YYMMDD
            until_date = datetime.date(int('20' + data[0][0:2]), int(data[0][2:4]), int(data[0][4:6]))
        
        if until_date:
            if until_date < from_date:
                # until_date before from_date, invalid, use only from_date
                until_date = None
                print('Invalid date interval given, only using first date as start date.')


'''
Analyze data
'''
# Get data, split over lines
source_file = open("yrla_logg.txt", 'r')
source_lines = source_file.read().splitlines()
source_file.close()

# Remove trailing \n and \t
for i in range(len(source_lines)):
    source_lines[i] = source_lines[i].strip().lower()

# Extract and remove header line
header_line = source_lines.pop(0)

# Get all entries
log_entries = []
for line in source_lines:
    entry = LogEntry(re.split(r'\t+', line))
    log_entries.append(entry)

# Sort all entries based on meter value, and if equal, if drive is starting or ending
# Should produce a list with rising meter values, and ending drives before starting if meter value equal
log_entries.sort(key = lambda entry: (entry.meter, entry.isStarting))

# Remove entries outside of from-until interval
log_entries = [entry for entry in log_entries if entry.dateInInterval(from_date, until_date)]

'''
for entry in log_entries:
    entry.printEntry()
    print('')'''

# Assuming first entry isStarting == True
organization_drives = {}
private_drives = {}
drive_is_started = False
start_entry = LogEntry()
end_entry = LogEntry()
for entry in log_entries:
    if (not drive_is_started) and entry.isStarting:
        # No drive started, and next isStarting == True
        start_entry.copyValues(entry)
        drive_is_started = True

    elif (not drive_is_started) and (not entry.isStarting) and end_entry:
        # No drive started, and ending drive, but have previous drive
        if not (entry.meter > end_entry.meter):
            # Double end, no increase in meter, skip this
            continue

        # If not double, assume driver forgot to start journey
        # Use meter from previous drive but all other data from the end entry
        start_entry.copyValues(entry)
        start_entry.meter = end_entry.meter
        end_entry.copyValues(entry)
        drive = Drive(start_entry, end_entry)
        if drive.renter in ['privat', 'Privat', 'PRIVAT']:
            if drive.driver in private_drives:
                private_drives[drive.driver].append(drive)
            else:
                private_drives[drive.driver] = [drive]
        else:
            if drive.renter in organization_drives:
                organization_drives[drive.renter].append(drive)
            else:
                organization_drives[drive.renter] = [drive]
        drive_is_started = False

    elif (not drive_is_started) and (not entry.isStarting) and (not end_entry):
        # No drive started, and ending drive, and have no previous drive
        # Can only happen for first entries
        # TODO: Handle this, not handled now
        continue

    elif drive_is_started and (not entry.isStarting):
        # Drive started, and next is ending
        
        # Check if actually driven anything, or problem with the sorting
        if not (entry.meter > start_entry.meter):
            if not (entry.renter == start_entry.renter):
                # no change in meter but different renter
                # problem i sorting, skip this
                continue

        # End drive
        end_entry.copyValues(entry)
        drive = Drive(start_entry, end_entry)
        if drive.renter in ['privat', 'Privat', 'PRIVAT']:
            if drive.driver in private_drives:
                private_drives[drive.driver].append(drive)
            else:
                private_drives[drive.driver] = [drive]
        else:
            if drive.renter in organization_drives:
                organization_drives[drive.renter].append(drive)
            else:
                organization_drives[drive.renter] = [drive]
        drive_is_started = False

    elif drive_is_started and (entry.isStarting):
        # Drive started, but another start. Check if double or forgot to end.
        if not (entry.meter > start_entry.meter):
            # Double start, no increase in meter, skip this
            continue

        # If not double, assume previous driver forgot to end journey
        # Use meter from this drive but other data from previous drive to end it
        end_entry.copyValues(start_entry)
        end_entry.meter = entry.meter
        drive = Drive(start_entry, end_entry)
        if drive.renter in ['privat', 'Privat', 'PRIVAT']:
            if drive.driver in private_drives:
                private_drives[drive.driver].append(drive)
            else:
                private_drives[drive.driver] = [drive]
        else:
            if drive.renter in organization_drives:
                organization_drives[drive.renter].append(drive)
            else:
                organization_drives[drive.renter] = [drive]

        # Start the new journey
        start_entry.copyValues(entry)
        drive_is_started = True

    else:
        # Should not be here! Or might have missed a case!
        print("Something went wrong trying to get the drives.")
        print("The current entry:")
        entry.printEntry()

'''
print('************************')
# Done getting all drives
for driver, drives in private_drives.items():
    print(driver, "drove:")
    print('')
    for drive in drives:
        drive.printDrive()
    print('---------')

print('************************')
for renter, drives in organization_drives.items():
    print(renter, "drove:")
    print('')
    for drive in drives:
        drive.printDrive()
    print('---------')
print('************************')
'''

date = datetime.date(2018, 1, 12)

date_str = ''
if not from_date:
    from_date = log_entries[0].date
if not until_date:
    until_date = log_entries[len(log_entries) - 1].date

if from_date and until_date:
    date_str += str(from_date) + ' ' + chr(8211) + ' ' + str(until_date)
elif from_date:
    date_str += str(from_date) + ' ' + chr(8211)
elif until_date:
    date_str += chr(8211) + ' ' + str(until_date)

text = """<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="styles.css">
    <link rel="icon" href="ysektionen.ico">
    <title>Yrla Log Parser - Results</title>
</head>
<body>

    <h1>Yrla Log Parser - Results</h1>
    <h3>For dates: """ + date_str + """</h3>
    <p>My first paragraph.</p>

    <div>
        <h2>Drives when rented by organizations</h2>
        <table style="width:700px">
            <tr>
                <th></th>
                <th align="left">Date</th>
                <th align="left">Distance</th>
                <th align="left">Is member</th>
                <th align="left">Using towbar</th>
                <th align="left">Total price</th>
            </tr>
            """

for renter, drives in organization_drives.items():
    text += """
            <tr style="height:20px">
                <td colspan="6">
                    <div class="seperator-row">
                    </div>
                </td>
            </tr>
            <tr>
                <td><b>""" + drives[0].renter.upper() + """</b></td>
                <td>""" + str(drives[0].date) + """</td>
                <td align="right">""" + str(drives[0].distance) + """</td>
                <td align="center">""" + ('Yes' if drives[0].isMember else 'No') + """</td>
                <td align="center">""" + ('Yes' if drives[0].usingTowbar else 'No') + """</td>
                <td align="right">""" + str(drives[0].getCost()) + """</td>
            </tr>"""
    if len(drives) > 1:
        text += """
            <tr>
                <td><a href="mailto:""" + drives[1].email + """">""" + drives[1].email + """</a></td>
                <td>""" + str(drives[1].date) + """</td>
                <td align="right">""" + str(drives[1].distance) + """</td>
                <td align="center">""" + ('Yes' if drives[1].isMember else 'No') + """</td>
                <td align="center">""" + ('Yes' if drives[1].usingTowbar else 'No') + """</td>
                <td align="right">""" + str(drives[1].getCost()) + """</td>
            </tr>"""
        if len(drives) > 2:
            for drive in drives[2:]:
                text += """
            <tr>
                <td></td>
                <td>""" + str(drive.date) + """</td>
                <td align="right">""" + str(drive.distance) + """</td>
                <td align="center">""" + ('Yes' if drive.isMember else 'No') + """</td>
                <td align="center">""" + ('Yes' if drive.usingTowbar else 'No') + """</td>
                <td align="right">""" + str(drive.getCost()) + """</td>
            </tr>"""
    else:
        text += """
            <tr>
                <td><a href="mailto:""" + drives[0].email + """">""" + drives[0].email + """</a></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
            </tr>"""

text += """
            <tr style="height:20px">
                <td colspan="6">
                    <div class="seperator-row">
                    </div>
                </td>
            </tr>
        </table>
    </div>
    <div>
        <h2>Drives when rented by private persons</h2>
        <table style="width:700px">
            <tr>
                <th></th>
                <th align="left">Date</th>
                <th align="left">Distance</th>
                <th align="left">Is member</th>
                <th align="left">Using towbar</th>
                <th align="left">Total price</th>
            </tr>
            """

for driver, drives in private_drives.items():
    text += """
            <tr style="height:20px" class="seperator-row">
                <td colspan="6">
                    <div class="seperator-row">
                    </div>
                </td>
            </tr>
            <tr>
                <td><b>""" + drives[0].driver.title() + """</b></td>
                <td>""" + str(drives[0].date) + """</td>
                <td align="right">""" + str(drives[0].distance) + """</td>
                <td align="center">""" + ('Yes' if drives[0].isMember else 'No') + """</td>
                <td align="center">""" + ('Yes' if drives[0].usingTowbar else 'No') + """</td>
                <td align="right">""" + str(drives[0].getCost()) + """</td>
            </tr>"""
    if len(drives) > 1:
        text += """
            <tr>
                <td><a href="mailto:""" + drives[1].email + """">""" + drives[1].email + """</a></td>
                <td>""" + str(drives[1].date) + """</td>
                <td align="right">""" + str(drives[1].distance) + """</td>
                <td align="center">""" + ('Yes' if drives[1].isMember else 'No') + """</td>
                <td align="center">""" + ('Yes' if drives[1].usingTowbar else 'No') + """</td>
                <td align="right">""" + str(drives[1].getCost()) + """</td>
            </tr>"""
        if len(drives) > 2:
            for drive in drives[2:]:
                text += """
            <tr>
                <td></td>
                <td>""" + str(drive.date) + """</td>
                <td align="right">""" + str(drive.distance) + """</td>
                <td align="center">""" + ('Yes' if drive.isMember else 'No') + """</td>
                <td align="center">""" + ('Yes' if drive.usingTowbar else 'No') + """</td>
                <td align="right">""" + str(drive.getCost()) + """</td>
            </tr>"""
    else:
        text += """
            <tr>
                <td><a href="mailto:""" + drives[0].email + """">""" + drives[0].email + """</a></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
                <td></td>
            </tr>"""

text += """
            <tr style="height:20px">
                <td colspan="6">
                    <div class="seperator-row">
                    </div>
                </td>
            </tr>
        </table>
    </div>
</body>
</html>"""


result_file = open('yrla_drives.html', 'w')
result_file.write(text)

webbrowser.open_new_tab('yrla_drives.html')


result_file.close()