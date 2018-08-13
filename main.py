
import re
from log_entry import LogEntry
from drive import Drive

# Get data, split over lines
file_source = open("yrla_logg.txt")
source_lines = file_source.read().splitlines()

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

# Sort all entries based on meter value
log_entries.sort(key = lambda entry: entry.meter)

'''for entry in log_entries:
    entry.printEntry()
    print('')'''

# Assuming first entry isStarting == True
organization_drives = {}
private_drives = {}
drive_is_started = False
start_entry = None
end_entry = None
for entry in log_entries:
    if (not drive_is_started) and entry.isStarting:
        # No drive started, and next isStarting == True
        start_entry = entry
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
        end_entry = entry
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
