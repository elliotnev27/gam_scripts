#!/usr/bin/env python3

#
# get all the groups and their memebers to create a CSV for the address book.
# this handles nested groups
#

import argparse
import collections
import re
import subprocess
import sys
import os

BLOCK_LIST = ['owners@cuttersstudios.com', 'skii@cutters.com', 'thursday@cuttersstudios.com', 'tumblr@cuttersstudios.com', 'twitter@cuttersstudios.com', 'uberconference@cuttersstudios.com', 'vimeo@cuttersstudios.com', 'vultr@cuttersstudios.com', 'webflow@cuttersstudios.com', 'webmaster@cuttersstudios.com', 'wordpress@cuttersstudios.com']
BLOCK_REGEX = [r'(?i)^c\d+@cuttersstudios.com', r'(?i)^zcc\d+@cuttersstudios.com', r'(?i)gsg\d+@flavor.tv', r'(?i)sling\d', r'(?i)slingbox']

HOME = os.path.expanduser("~")
GAM = os.path.join(HOME, 'bin/gamadv-xtd3/gam')
MAX_DEPTH = 10

def get_args():
    parser = argparse.ArgumentParser(description='Get CSVs of Cutters Studios groups for address book or for fun.')
    parser.add_argument('groups', nargs='*', help='List of groups to query. If not specified all groups will be queried.')
    parser.add_argument('--verbose', '-v', action='store_true', help='Shell output talks a lot.')
    parser.add_argument('--debug', '-d', action='store_true', help='Shell outputs debugging information.')
    parser.add_argument('--output_path', '-o', type=str, help='Write csv files to directory')

    args = parser.parse_args()

    if args.debug:
        args.verbose = True

    if not args.output_path:
        args.output_path = os.path.join(HOME, 'Desktop', 'csv')
    
    return args

def check_output_path(csv_dir):
    if not os.path.isdir(csv_dir):
        print(f'[FATAL] {csv_dir} is not a directory!')
        sys.exit(1)

def get_group_list():
    print('[INFO] Getting group names... This may take awhile...')
    group_list_output = subprocess.Popen([GAM, 'print', 'groups'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf8')
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

def get_group_members(group_name, args):
    print(f'[INFO] Getting group info for: {group_name}')
    group_output = subprocess.Popen([GAM, 'info', 'group', group_name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf8')
    group_output = group_output.communicate()[0]

    for group_line in group_output.splitlines():
        group_line = group_line.lstrip()
        group_line = group_line.rstrip()

        if args.debug:
            print(f'[DEBUG] {group_line}')

        try:
            email_address = re.findall(r'(?i)[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', group_line)[0]
        except(IndexError):
            if args.debug:
                print('[DEBUG] Skipping because line does not contain an email address.')
            continue

        if email_address in BLOCK_LIST:
            if args.debug:
                print('[DEBUG] Skipped due to blocklist.')
            continue
        if email_address.startswith('xx-'):
            if args.debug:
                print('[DEBUG] Skipping due to starting with xx-')
            continue
        if re.search(r'(?i)@temp\.', email_address) or re.search(r'(?i)@temp\.', group_name):
            if args.debug:
                print('[DEBUG] Skipping due to temp address.')
            continue
        if re.search(r'(?i)@archive\.', email_address) or re.search(r'(?i)@archive\.', group_name):
            if args.debug:
                print('[DEBUG] Skipping due to archive address.')
            continue
        if re.search(r'(?i)name:\s+fwd:', group_line):
            if args.debug:
                print('[DEBUG] Skipping due to mail forward.')
            break
        if not re.search(r'(?i)member:', group_line) and not re.search(r'(?i)owner:', group_line) and not re.search(r'(?i)manager:', group_line):
            if args.debug:
                print('[DEBUG] Not a member line')
            continue

        if args.debug:
            print(f'[DEBUG] {email_address}')

        yield email_address

def write_csv(address_book, args):
    print('[INFO] Writing csv files...')
    for key, vals in address_book.items():
        vals.sort()
        csv_file_path = os.path.join(args.output_path, f'{key}.csv')
        if not vals:
            continue
        with open(csv_file_path, 'w') as csv_file:
            if args.verbose:
                print(f'[INFO] Writing to {csv_file_path}')
            for cur_val in vals:
                csv_file.write('{}\n'.format(cur_val))
                if args.debug:
                    print(f'[DEBUG] {cur_val}')

def main():
    args = get_args()
    check_output_path(args.output_path)
    address_book = collections.defaultdict(list)

    if not args.groups:
        group_list = get_group_list()
    else:
        group_list = args.groups

    for group_name in group_list:
        for group_member in get_group_members(group_name, args):
            if args.debug:
                print(f'[DEBUG] {group_member}')
            if not group_member:
                if args.debug:
                    print(f'[DEBUG] {group_member}')
                continue
            if group_member not in address_book[group_name]:
                if args.debug or args.verbose:
                    print(f'[INFO] Adding {group_member} to {group_name}')
                address_book[group_name].append(group_member)

    write_csv(address_book, args)

if __name__ == '__main__':
    main()

sys.exit(0)
