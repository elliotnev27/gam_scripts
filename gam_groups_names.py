#!/usr/bin/env python

#
# change permissions of all groups to match our proper permissions
#

import re
import subprocess
import time
import sys
import os

HOME = os.path.expanduser("~")
GAM = os.path.join(HOME, 'bin/gam/gam')

print('[INFO] Getting group names... This may take awhile...')
group_output = subprocess.Popen([GAM, 'print', 'groups'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
group_output = group_output.communicate()[0]
group_list = []

for group_name in group_output.splitlines():
    try:
        if re.findall(r'(?i)^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', group_name)[0] != group_name:
            continue
    except IndexError:
        continue

    group_list.append(group_name)

sys.exit(0)
