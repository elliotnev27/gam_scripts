#!/usr/bin/env python

import subprocess
import re
import collections
import os
import sys

if not os.path.isdir(sys.argv[1]):
    print('[FATAL] Must specify directory for csv file to be written.')
    sys.exit(1)

calendar_db = collections.defaultdict(list)
gam = '/Users/elliot/bin/gam/gam'

all_users_output = subprocess.Popen([gam, 'print', 'users'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
all_users_output = all_users_output.communicate()[0].split('\n')[3:]
	
for cur_user in all_users_output:
	if not cur_user:
		continue
	if cur_user.startswith('xx-'):
		continue
		
	print('Current user: {}'.format(cur_user))
	
	calendar_output = subprocess.Popen([gam, 'user', cur_user, 'show', 'calendars'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	for cur_line in calendar_output.communicate()[0].split('\n'):
		if re.search(r'(?i)Calendar: ', cur_line):
			calendar_id = cur_line.replace('Calendar: ', '')
			calendar_id = re.sub(r' \(\d+/\d+\)', '', calendar_id)
			calendar_id = calendar_id.replace(' ', '')
			calendar_dict = {}
			calendar_dict['id'] = calendar_id
			continue
			
		if re.search(r'(?i)Summary: ', cur_line):
			summary_line = cur_line.replace('    Summary: ', '')
                        summary_line = summary_line.strip(',')
			calendar_dict['summary'] = summary_line
			continue
			
		if re.search(r'(?i)Access Level: ', cur_line):
			access_line = cur_line.replace('    Access Level: ', '')
			calendar_dict['access'] = access_line
			calendar_db[cur_user].append(calendar_dict)
			continue

csv_path = os.path.join(sys.argv[1], 'calendar_ids.csv')
with open(csv_path, 'w') as open_file:
    open_file.write('user,calendar_name,id,access\n')
    for cur_user, user_calendars in calendar_db.items():
        print('\nCurrent User: {}'.format(cur_user))
	for cur_user_calendar in user_calendars:
		open_file.write('{},{},{},{}\n'.format(cur_user, cur_user_calendar['summary'], cur_user_calendar['id'], cur_user_calendar['access']))
		print('summary: {}'.format(cur_user_calendar['summary']))
		print('id: {}'.format(cur_user_calendar['id']))
		print('access: {}'.format(cur_user_calendar['access']))
		

