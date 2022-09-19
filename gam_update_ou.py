#!/usr/bin/env python3

import os
import csv
import subprocess
import sys

home = os.path.expanduser("~")
gam = os.path.join(home, 'bin/gamadv-xtd3/gam')

csv_path = sys.argv[1]
with open(csv_path) as file:
    reader = csv.DictReader(file)
    for row in reader:
        email = row['Email Address [Required]']
        ou = row['Org Unit Path [Required]']
        print(f'[INFO] Change {email} to {ou}')
        try:
            subprocess.check_call([gam, 'update', 'org', ou, 'add', 'users', email])
        except(subprocess.CalledProcessError, IOError) as error_info:
            
            print(error_info)
            print(f'[FATAL] Error on {email}')
            sys.exit(1)