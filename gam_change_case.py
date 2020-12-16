#!/usr/bin/env python3

#
# people aren't perfect. sometimes they don't capitalize proper nouns. it's probably a programmer trying to admin
# luckily computer can help fix everyone's name to be like John Doe.
#

import os
import subprocess
import sys

HOME = os.path.expanduser('~')
GAM = os.path.join(HOME, 'bin/gamadv-xtd3/gam')

output = subprocess.Popen([GAM, 'report', 'users'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
output = output.communicate()[0]
output = output.decode('utf-8')

for line in output.split('\n')[1:]:
    try:
        email = line.split(',')[0]
        first = line.split(',')[6]
        last = line.split(',')[13]
        if first == 'accounts:first_name':
            continue
        if last == 'accounts:last_name':
            continue
        if first[0].isupper() and last[0].isupper():
            continue

        first = f'{str.upper(first[0])}{str.lower(first[1:])}'
        last = f'{str.upper(last[0])}{str.lower(last[1:])}'
        print(f'{email},{first},{last}')
    except(IndexError):
        continue

    try:
        subprocess.check_call([GAM, 'update', 'user', email, 'firstname', first, 'lastname', last])
    except(subprocess.CalledProcessError, IOError) as error_info:
        print(error_info)
        print(f'[FATAL] Did not update {email}')

