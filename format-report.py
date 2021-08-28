#!/usr/bin/env python3

# Autorank backup formatter script written by DiaDemiEmi

import re
import os
import sys
import csv
import fnmatch
import calendar
from operator import itemgetter
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
usermap_location = os.getenv('USERMAP_LOCATION')
backup_location = os.getenv('BACKUPS_LOCATION')
output_location = os.getenv('REPORTS_OUTPUT_LOCATION')
verbose = os.getenv('VERBOSE')

# Create REPORTS_OUTPUT_LOCATION if it does not exist
if not os.path.exists(output_location):
    os.makedirs(output_location)

# Function to convert minutes into a human readable DAYS:HOURS:MINUTES
def timeformat(min):
    days = min // 1440
    min = min % 1440
    hours = min // 60
    min = min % 60
    minutes = min % 60
    return("{0}:{1}:{2}".format(days, hours, minutes))

# Search for all backup files and store a list of them
files = os.listdir(backup_location)

# Define function to format the backup. 
def formatbackup(file_prefix):
    # Scan for which backup to use
    filelist = []
    for entry in files:
        if fnmatch.fnmatch(entry, "{0}_time-backup-*.yml".format(file_prefix)):
            filelist.append(entry)
    filelist.sort(reverse=True)

    # Create a list which will contain other lists with data of players
    datalist = []

    if verbose == "true":
        print("Found file {0}/{1}".format(backup_location, filelist[0]))

    # Reads the backup file one line at a time, fetching the UUID and using it to read the associated 
    # Essentials userdata YML file. From this it reads the username of the account which it appends to 
    # a temporary list with the total minutes, username and human readable playtime. 
    # This list is then added to a larger list of lists which is sorted and written into a file.
    with open(os.path.join(backup_location, filelist[0])) as backup, open (os.path.join(usermap_location), newline='') as usermap:
        reader = csv.reader(usermap, delimiter=',')
        for count, line in enumerate(backup):
            uuid = re.findall('^[^:]+', line)[0]
            totalminutes = int(re.findall('(?<=: ).*', line)[0])

            for row in reader:
                if uuid == row[1]:
                    lastaccountname = row[0]
                    usermap.seek(0)
                    break;

            playtime = timeformat(totalminutes)
            tmplist = []
            tmplist.extend([totalminutes, lastaccountname, playtime])
            datalist.append(tmplist)
            if verbose == "true":
                print(tmplist)

    # This sorts the list of lists by the players which have the most playtime
    sorted_datalist = reversed(sorted(datalist, key=itemgetter(0)))

    # Begin writing to file
    with open("{0}/{1}_{2}-Report.txt".format(output_location, datetime.today().date(), file_prefix), 'w') as output:
        if verbose == "true":
            print("Writing to file {0}!".format(output.name))
        output.write("# USERNAME: DAYS:HOURS:MINUTES \n\n")
        for i in sorted_datalist:
            output.write("{0}: {1}\n".format(i[1],i[2]))
        if verbose == "true":
            print("Finished! Exiting...")

if len(sys.argv) > 1:
    possible_args = ["Daily", "Weekly", "Monthly", "Total"]
    if sys.argv[1] in possible_args:
        if verbose == "true":
            print("Creating a {} report".format(sys.argv[1]))
        formatbackup(sys.argv[1])
else:
    # Run the function with the "Daily" prefix
    if verbose == "true":
        print("Creating a Daily report")
    formatbackup("Daily")

    # Check if it is a saturday
    # If it is a saturday, run the function with the "Weekly" prefix
    if verbose == "true":
        print("Creating a Weekly report")
    if datetime.today().date().weekday == 5:
        formatbackup("Weekly")

    # Check if it is the last day of the month
    # If it is the last day of the month, run the function with the "Monthly" prefix
    if verbose == "true":
        print("Creating a Monthly report")
    if datetime.today().date().day == calendar.monthrange(datetime.today().date().year, datetime.today().date().month)[1]:
        formatbackup("Monthly")
