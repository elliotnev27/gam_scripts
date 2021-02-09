#!/usr/bin/env python

#
# Creates csv of all the calendars users has access to with their access level
#

import subprocess
import re
import collections
import os
import sys

if not os.path.isdir(sys.argv[1]):
    print('[FATAL] Must specify directory for csv file to be written.')
    sys.exit(1)

calendar_db = collections.defaultdict(list)
home = os.path.expanduser("~")
gam = os.path.join(home, 'bin/gamadv-xtd3/gam')

all_users_output = subprocess.Popen([gam, 'print', 'users'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
all_users_output = all_users_output.communicate()[0].split('\n')[3:]

csv_path = os.path.join(sys.argv[1], 'calendars.csv')
with open(csv_path, 'w') as open_file:
	open_file.write('calendarId,id,role,scope.type,scope.value\n')

	for cur_user in all_users_output:
		if not cur_user:
			continue
		if cur_user.startswith('xx-'):
			continue
			
		print('Current user: {}'.format(cur_user))
		
		calendar_output = subprocess.Popen([gam, 'calendar', cur_user, 'printacl'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for cur_line in calendar_output.communicate()[0].split('\n'):
			cur_line = cur_line.strip('\n')
			if re.search(r'(?i)Getting Calendar ACLs for ', cur_line):
				continue
			if re.search(r'(?i)calendarId,id,role,scope\.type,scope\.value', cur_line):
				continue
			if not cur_line:
				continue

			open_file.write('{}\n'.format(cur_line))

sys.exit(0)
