#!/usr/bin/env python

#
# script to offboard user. Once run there email will be ready to archive. Then delete.
#
# 1) generate & set a pseudo random password 
# 2) change organization unit to offboarding
# 3) invalidate previous oath tokens & 2fa backup codes
# 4) disable the user
# 5) remove user from groups
# 6) rename user to have xx- prefix
# 7) remove alias of original email address
#
# TODO:
# Add option for GYB mail backup
# Add option to delete user entirely
#


import argparse
import os
import sys
import re
import random
import string
import time
import subprocess

HOME = os.path.expanduser("~")
GAM = os.path.join(HOME, 'bin/gamadv-xtd3/gam')
DEFAULT_LOG_PATH = os.path.join(HOME, 'Desktop', 'offboarding.log')

PARSER = argparse.ArgumentParser(description='Renames user to have xx- suffix, changes password, terminates sessions, revokes OAUTH, and terminates current sessions.')
PARSER.add_argument('email', help='User address that will be offboarded.')
PARSER.add_argument('log', nargs='?', help='Log location other than default: {}'.format(DEFAULT_LOG_PATH))
PARSER.add_argument('-n', '--safe_log', action='store_true', help='Do not log new credentials in log file')
PARSER.add_argument('-s', '--secure', action='store_true', help='Do not output new password in shell or log.')
PARSER.add_argument('-v', '--verbose', action='store_true', help='Make this script talk a lot.')

ARGS = PARSER.parse_args()

if not ARGS.log:
    ARGS.log = DEFAULT_LOG_PATH

if ARGS.secure:
    ARGS.safe_log = True


LOG_DIR = os.path.dirname(ARGS.log)
if not os.path.exists(LOG_DIR):
    print('[CRITICAL] {} does not exist.'.format(LOG_DIR))
    sys.exit(1)

def get_user_info():
    if not os.path.exists(GAM):
        print('[CRITICAL] GAM does not exist!')
        return False

    first_name = ''
    last_name = ''
    email_aliases = [ARGS.email]
    groups = []

    email_aliases_trip = False
    groups_trip = False
    proc = subprocess.Popen([GAM, 'info', 'user', ARGS.email], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    output = proc.communicate()[0]
    if proc.returncode != 0:
        print(proc.returncode)
        print('[CRITICAL] User does not exist or issue running GAM.')
        sys.exit(1)

    for line in filter(bool, output.splitlines()):
        if email_aliases_trip:
            if not re.search(r'(?i).+@.+\.com', line):
                email_aliases_trip = False
                continue
            line = line.replace('alias:', '')
            line = line.strip(' ')
            email_aliases.append(line)
            continue

        if groups_trip:
            try:
                group_name = re.findall('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', line)[0]
            except IndexError:
                groups_trip = False
                continue

            groups.append(line)
            continue

        if re.search(r'(?i)First Name:', line):
            first_name = re.sub(r'(?i)First Name: ', '', line)

            for x in first_name:
                if x != ' ':
                    break
                first_name = first_name[1:]

            continue
        if re.search(r'(?i)Last Name:', line):
            last_name = re.sub(r'(?i)Last Name: ', '', line)

            for x in last_name:
                if x != ' ':
                    break
                last_name = last_name[1:]

            continue
        if re.search(r'(?i)Email Aliases:', line):
            email_aliases_trip = True
            continue
        if re.search(r'(?i)Groups: \(\d+\)', line):
            groups_trip = True
            continue

    if not first_name and not last_name and not email_aliases and not groups:
        print('[CRITICAL] User does not exist! (empty)')
        sys.exit(1)

    print('''
   First Name: {}
    Last Name: {}

Email Aliases: {}
       Groups: {}
    '''.format(first_name, last_name, email_aliases, groups))

    return first_name, last_name, email_aliases, groups

def get_random_password():
    length = 12
    chars = '!#$%&()*+,-.0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_abcdefghijklmnopqrstuvwxyz{|}~'
    password = ''
    while len(password) < length:
        password += str(random.choice(chars))

    return password

def set_new_password(new_password):
    if ARGS.verbose:
        print('[INFO] Changing password of {} to {}'.format(ARGS.email, new_password))
    try:
        subprocess.check_call([GAM, 'update', 'user', ARGS.email, 'password', new_password])
        subprocess.check_call([GAM, 'update', 'user', ARGS.email, 'changepassword', 'on'])
        time.sleep(2)
        subprocess.check_call([GAM, 'update', 'user', ARGS.email, 'changepassword', 'off'])
    except(subprocess.CalledProcessError, IOError) as error_info:
        print(error_info)
        print('[CRITICAL] Failed to change password!')
        sys.exit(1)

    return True

def change_ou():
    if ARGS.verbose:
        print('[INFO] Changing OU of {} to offboarding.'.format(ARGS.email))
    try:
        subprocess.check_call([GAM, 'update', 'org', 'offboarding', 'add', 'users', ARGS.email])
    except(subprocess.CalledProcessError, IOError) as error_info:
        print(error_info)
        print('[WARN] Cannot change OU of {}'.format(ARGS.email))

def reset_tokens():
    if ARGS.verbose:
        print('[INFO] Resetting tokens for {}'.format(ARGS.email))
    try:
        subprocess.check_call([GAM, 'user', ARGS.email, 'deprovision'])
        subprocess.check_call([GAM, 'user', ARGS.email, 'update', 'backupcodes'])
    except(subprocess.CalledProcessError) as error_info:
        print(error_info)
        print('[WARN] Failed deprovision/updating backup codes.')

    return True

def disable_user():
    try:
        if ARGS.verbose:
            print('[INFO] Disabled email forwarding for {}'.format(ARGS.email))
        subprocess.check_call([GAM, 'user', ARGS.email, 'forward', 'off'])
        if ARGS.verbose:
            print('[INFO] Disabled imap for {}'.format(ARGS.email))
        subprocess.check_call([GAM, 'user', ARGS.email, 'imap', 'off'])
        if ARGS.verbose:
            print('[INFO] Disabled pop for {}'.format(ARGS.email))
        subprocess.check_call([GAM, 'user', ARGS.email, 'pop', 'off'])
        if ARGS.verbose:
            print('[INFO] Disabled gal for {}'.format(ARGS.email))
        subprocess.check_call([GAM, 'update', 'user', ARGS.email, 'gal', 'off'])
    except(subprocess.CalledProcessError) as error_info:
        print(error_info)
        sys.exit(1)

    return True

def remove_user_from_groups(group_list):
    return True

    if ARGS.verbose:
        print('[INFO] Removing {} from groups.'.format(ARGS.email))

    try:
        subprocess.check_call([GAM, 'delete', 'groups'])
    except(subprocess.CalledProcessError, IOError) as error_info:
        print(error_info)
        print('[WARN] Cannot delete {} from groups.'.format(ARGS.email))
        sys.exit(1)

    return True

def rename_user():
    if ARGS.verbose:
        print('[INFO] Renaming {} to xx-{}'.format(ARGS.email, ARGS.email))
    try:
        subprocess.check_call([GAM, 'update', 'user', ARGS.email, 'username', 'xx-{}'.format(ARGS.email)])
    except(subprocess.CalledProcessError, IOError) as error_info:
        print(error_info)
        print('[CRITICAL] Cannot rename {}'.format(ARGS.email))
        sys.exit(1)

    time.sleep(2)
    return True

def remove_aliases(email_aliases):
    if ARGS.verbose:
        print('[INFO] Removing aliases for account: {}'.format(ARGS.email))
    for cur_address in email_aliases:
        try:
            if ARGS.verbose:
                print('[INFO] Removing alias: {}'.format(cur_address))
            subprocess.check_call([GAM, 'delete', 'aliases', cur_address])
        except(subprocess.CalledProcessError, IOError) as error_info:
            print(error_info)
            print('[CRITICAL] Cannot delete aliases for {}'.format(ARGS.email))
            sys.exit(1)

    return True

def write_log(first_name, last_name, new_password):
    with open(ARGS.log, 'a+') as log_file:
        log_file.write('\n{},{},{},{}'.format(first_name, last_name, 'xx-{}'.format(ARGS.email), new_password))

    return True

def main():
    print('[INFO] Starting offboarding process...')
    first_name, last_name, email_aliases, groups = get_user_info()
    while True:
        try:
            cont = str.lower(raw_input('Do you want to continue offboarding (Y/N): '))
        except(TypeError):
            pass

        if cont in ['y', 'yes']:
            break

        if cont in ['n', 'no']:
            print('[INFO] Cancelled.')
            sys.exit(1)

    new_password = get_random_password()
    set_new_password(new_password)
    change_ou()
    reset_tokens()
    disable_user()
    remove_user_from_groups(groups)
    if not ARGS.email.startswith('xx-'):
        rename_user()
        remove_aliases(email_aliases)

    if not ARGS.secure:
        print('{},{},{},{}'.format(first_name, last_name, ARGS.email, new_password))

    if not ARGS.safe_log:
        write_log(first_name, last_name, new_password)

    print('[INFO] Offboarding done.')
    sys.exit(0)

if __name__ == '__main__':
    main()

