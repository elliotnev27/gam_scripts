#!/usr/bin/env python

import os
import subprocess
import re

GAM = '/Users/elliot/bin/gam/gam'
cal_dick = {}
with open('/Users/elliot/Desktop/calendar_2.csv', 'r') as open_file:
	for cur_line in open_file.read().splitlines():
		name, id = cur_line.split(',')
		cal_dick[name] = id

with open('/tmp/calendar_3.csv', 'w') as open_file:
	for name, id in cal_dick.items():
		if not name or not id:
			continue
	
		output = subprocess.Popen([GAM, 'calendar', id, 'printacl'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		for cur_line in output.communicate()[0].split('\n'):
			if cur_line == 'id,scope.type,scope.value,role':
				continue
			try:
				user = cur_line.split(',')[2]
			except(IndexError):
				continue
			
			print(user, name, id)
			open_file.write('{},{},{}\n'.format(user, name, id))

print('Done!')
			
