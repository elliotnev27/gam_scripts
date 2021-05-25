#!/usr/bin/env python

#
# change permissions of all groups to match our proper permissions
#

import collections
import re
import subprocess
import time
import sys
import os

BLOCK_LIST = ['thursday@cuttersstudios.com']

HOME = os.path.expanduser("~")
GAM = os.path.join(HOME, 'bin/gamadv-xtd3/gam')

print('[INFO] Getting group names... This may take awhile...')
group_list_output = subprocess.Popen([GAM, 'print', 'groups'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
group_list_output = group_list_output.communicate()[0]

group_list = []
address_book = collections.defaultdict(list)
for group_name in group_list_output.splitlines():
    if group_name.startswith('xx-'):
        continue
    if group_name in BLOCK_LIST:
        continue
    try:
        if re.findall(r'(?i)^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', group_name)[0] != group_name:
            continue
        group_list.append(group_name)
    except IndexError:
        continue

for group_name in group_list:
    print('[INFO] Getting group info for: {}'.format(group_name))
    group_output = subprocess.Popen([GAM, 'info', 'group', group_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    group_output = group_output.communicate()[0]

    for group_line in group_output.splitlines():
        if re.search(r'(?i)^\s+name:\s+fwd:', group_line):
            #print('[DEBUG] skip')
            continue
        if not re.search(r'(?i)^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', group_line):
            continue

        group_line = re.sub(r'(?i)^\s+member:\s+', '', group_line)
        group_line = re.sub(r'(?i)\s+\(group\)$', '', inner_group)
        if group_line in BLOCK_LIST:
            continue
        if group_line.startswith('xx-'):
            continue

        address_book[group_name].append(group_line)

#
# search collection for group addresses
#
for group_name, email_addresses in address_book:
    print('[INFO] Checking for nested groups in {}'.format(group_name))
    for cur_email in email_addresses:
        if cur_email in BLOCK_LIST:
            continue
        if cur_email not in group_list:
            continue
        email_addresses.remove(cur_email)
        for new_address in address_book[cur_email]:
            if new_address in BLOCK_LIST:
                continue
            if new_address.startswith('xx-'):
                continue
            if new_address in address_book[cur_email]:
                continue
            email_addresses.append(new_address)

        address_book[group_name] = email_addresses

print(address_book)
sys.exit(0)

