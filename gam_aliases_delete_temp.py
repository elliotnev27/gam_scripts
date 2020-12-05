#!/usr/bin/env python

import subprocess
import sys
import re

home = os.path.expanduser("~")
gam = os.path.join(home, 'bin/gam/gam')

users_output = subprocess.Popen([gam, 'print', 'users', 'aliases'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
users_output = users_output.communicate()[0].split('\n')

temp_addresses = []
for cur_user in users_output:
    vals = cur_user.split(',')
    for cur_val in vals:
        if not cur_val:
            continue
        if not re.search(r'@temp\.[A-Za-z]+\.[A-Za-z]+', cur_val):
            continue

        print(cur_val)
        subprocess.call([gam, 'delete', 'alias', cur_val])

