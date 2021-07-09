#!/usr/bin/env python

#
# get all the groups and their memebers to create a CSV for the address book.
# this handles nested groups
#

import collections
import re
import subprocess
import time
import sys
import os

BLOCK_LIST = ['', '']
BLOCK_REGEX = [r'', r'', r'']

HOME = os.path.expanduser("~")
GAM = os.path.join(HOME, 'bin/gamadv-xtd3/gam')
MAX_DEPTH = 10


def get_group_list():
    print('[INFO] Getting group names... This may take awhile...')
    group_list_output = subprocess.Popen([GAM, 'print', 'groups'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    group_list_output = group_list_output.communicate()[0]

    group_list = []
    for group_name in group_list_output.splitlines():
        if group_name.startswith('xx-'):
            continue
        if group_name in BLOCK_LIST:
            continue
        
        regex_blocked = False
        for cur_regex in BLOCK_REGEX:
            if re.search(r'{}'.format(cur_regex), group_name):
                regex_blocked = True
                break
        
        if regex_blocked:
            continue

        try:
            if re.findall(r'(?i)^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', group_name)[0] != group_name:
                continue
            group_list.append(group_name)
        except IndexError:
            continue
    
    return group_list

def get_group_members(group_name, depth):
    depth += 1
    if depth >= MAX_DEPTH:
        yield None
    print('[INFO] Getting group info for: {}'.format(group_name))
    group_output = subprocess.Popen([GAM, 'info', 'group', group_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    group_output = group_output.communicate()[0]

    for group_line in group_output.splitlines():
        group_line = group_line.lstrip()
        group_line = group_line.rstrip()

        try:
            email_address = re.findall(r'(?i)[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', group_line)[0]
        except(IndexError):
            #print('[DEBUG] Skipping because line does not contain an email address.')
            continue

        if email_address in BLOCK_LIST:
            #print('[DEBUG] Skipped due to blocklist.')
            continue
        if email_address.startswith('xx-'):
            #print('[DEBUG] Skipping due to starting with xx-')
            continue

        if re.search(r'(?i)Group:', group_line):
            continue

        if re.search(r'(?i) \(group\)', group_line):
            #print('[DEBUG] {}, {}'.format(email_address, depth))
            for cur_email in get_group_members(email_address, depth):
                yield cur_email
            continue

        #print('[DEBUG] {}, {}'.format(email_address, depth))
        yield email_address

def write_csv(address_book):
    for key, vals in address_book.items():
        csv_file_path = os.path.join(HOME, '{}.csv'.format(key))
        if not vals:
            continue
        with open(csv_file_path, 'w') as csv_file:
            for cur_val in vals:
                csv_file.write('{}\n'.format(cur_val))

def main():
    address_book = collections.defaultdict(list)

    for group_name in get_group_list():
        depth = 0
        for group_member in get_group_members(group_name, depth):
            if not group_member:
                continue
            if group_member not in address_book[group_name]:
                address_book[group_name].append(group_member)
    
    write_csv(address_book)

if __name__ == '__main__':
    main()

sys.exit(0)

