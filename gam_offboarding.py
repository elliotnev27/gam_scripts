#!/usr/bin/env python3

"""
script to offboard user. Once run there email will be ready to archive.

 1) generate & set a pseudo random password
 2) change organization unit to offboarding
 3) invalidate previous oath tokens & 2fa backup codes
 4) disable the user
 5) remove user from groups
 6) rename user to have xx- prefix
 7) remove alias of original email address (fails silently usually)
"""

import argparse
import os
import sys
import re
import random
import time
import subprocess

HOME = os.path.expanduser("~")
GAM = os.path.join(HOME, 'bin/gamadv-xtd3/gam')
DEFAULT_LOG_PATH = os.path.join('/var/log/offboarding.log')

PARSER = argparse.ArgumentParser(description='Follows offboarding procedure for Google Workplace')
PARSER.add_argument('email', help='User address that will be offboarded.')
PARSER.add_argument('log', nargs='?', help=f'Log location other than default: {DEFAULT_LOG_PATH}')
PARSER.add_argument('--nr', action='store_true', help='Do not rename user with xx- suffix')
PARSER.add_argument('-n', '--safe_log', action='store_true',
                    help='Do not log new credentials in log file')
PARSER.add_argument('-s', '--secure', action='store_true',
                    help='Do not output new password in shell or log.')
PARSER.add_argument('-y', '--yes', action='store_true', help='Do not prompt for confirmation.')
PARSER.add_argument('-v', '--verbose', action='store_true', help='Make this script talk a lot.')

ARGS = PARSER.parse_args()

if not ARGS.log:
    ARGS.log = DEFAULT_LOG_PATH

if ARGS.secure:
    ARGS.safe_log = True


LOG_DIR = os.path.dirname(ARGS.log)
if not os.path.exists(LOG_DIR):
    print(f'[CRITICAL] {LOG_DIR} does not exist.')
    sys.exit(1)

def get_user_info() -> tuple:
    """
    Get user's name, aliases, groups

    Returns:
        firstname: str, lastname: str, aliases: list, groups: list
    """
    if not os.path.exists(GAM):
        print('[CRITICAL] GAM does not exist!')
        return False

    first_name = ''
    last_name = ''
    email_aliases = [ARGS.email]
    groups = []

    email_aliases_trip = False
    groups_trip = False
    proc = subprocess.Popen([GAM, 'info', 'user', ARGS.email],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    output = proc.communicate()[0].decode("utf-8")
    if proc.returncode != 0:
        print(proc.returncode)
        print('[CRITICAL] User does not exist or issue running GAM.')
        sys.exit(1)

    for line in output.splitlines():
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
                group_name = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', line)[0]
                groups.append(group_name)
            except IndexError:
                groups_trip = False
                continue

            continue

        if re.search(r'(?i)First Name:', line):
            first_name = re.sub(r'(?i)First Name: ', '', line)

            for char in first_name:
                if char != ' ':
                    break
                first_name = first_name[1:]

            continue
        if re.search(r'(?i)Last Name:', line):
            last_name = re.sub(r'(?i)Last Name: ', '', line)

            for char in last_name:
                if char != ' ':
                    break
                last_name = last_name[1:]

            continue

        if re.search(r'(?i)Email Aliases:', line):
            email_aliases_trip = True
            continue
        if re.search(r'(?i)Groups:\s+\(\d+\)', line):
            groups_trip = True
            continue

    if not first_name and not last_name and not email_aliases and not groups:
        print('[CRITICAL] User does not exist! (empty)')
        sys.exit(1)

    print(f'''
   First Name: {first_name}
    Last Name: {last_name}

Email Aliases: {email_aliases}
       Groups: {groups}
    ''')

    return first_name, last_name, email_aliases, groups

def get_random_password() -> str:
    """
    Makes a random enough password
    """
    length = 16
    chars = '=,!#$%&()*+-.0123456789:;<>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[]^_abcdefghijklmnopqrstuvwxyz{|}~'
    password = ''
    while len(password) < length:
        if len(password) != 0:
            new_char = str(random.choice(chars))
        else:
            new_char = str(random.choice(chars[2:]))

        password += new_char

    return password

def set_new_password(new_password: str) -> bool:
    """
    args:
        new_password (str): password you want to set for the user

    returns:
        bool: True if successful
    """
    if ARGS.verbose:
        print(f'[INFO] Changing password of {ARGS.email} to {new_password}')
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

def change_ou() -> bool:
    """
    Change organizational Unit to cuttersstudios/offboarding

    Returns:
        bool: true if successful
    """

    if ARGS.verbose:
        print(f'[INFO] Changing OU of {ARGS.email} to offboarding.')
    try:
        subprocess.check_call([GAM, 'update', 'org', 'offboarding', 'add', 'users', ARGS.email])
    except(subprocess.CalledProcessError, IOError) as error_info:
        print(error_info)
        print(f'[WARN] Cannot change OU of {ARGS.email}')

    return True

def reset_tokens() -> True:
    """
    Removes 2FA backup codes and removes OAUTH tokens
    """
    if ARGS.verbose:
        print(f'[INFO] Resetting tokens for {ARGS.email}')
    try:
        subprocess.check_call([GAM, 'user', ARGS.email, 'deprovision'])
        subprocess.check_call([GAM, 'user', ARGS.email, 'delete', 'backupcodes'])
        subprocess.check_call([GAM, 'user', ARGS.email, 'update', 'backupcodes'])
    except(subprocess.CalledProcessError) as error_info:
        print(error_info)
        print('[WARN] Failed deprovision/updating backup codes.')

    return True

def disable_user() -> bool:
    """
    Removes email forwarding, IMAP, POP, Global Address List

    Returns:
        Bool: True if successful
    """
    try:
        if ARGS.verbose:
            print(f'[INFO] Disabled email forwarding for {ARGS.email}')
        subprocess.check_call([GAM, 'user', ARGS.email, 'forward', 'off'])
        if ARGS.verbose:
            print(f'[INFO] Disabled IMAP for {ARGS.email}')
        subprocess.check_call([GAM, 'user', ARGS.email, 'imap', 'off'])
        if ARGS.verbose:
            print(f'[INFO] Disabled POP for {ARGS.email}')
        subprocess.check_call([GAM, 'user', ARGS.email, 'pop', 'off'])
        if ARGS.verbose:
            print(f'[INFO] Disabled gal for {ARGS.email}')
        subprocess.check_call([GAM, 'update', 'user', ARGS.email, 'gal', 'off'])
    except(subprocess.CalledProcessError) as error_info:
        print(error_info)
        sys.exit(1)

    return True

def remove_user_from_groups(group_list:list) -> bool:
    """
    Args:
        group_list (str): list of groups you want the user removed from

    Returns
        bool: True if successful
    """
    if ARGS.verbose:
        print(f'[INFO] Removing {ARGS.email} from groups.')

    for cur_group in group_list:
        try:
            subprocess.check_call([GAM, 'update', 'group', cur_group, 'remove', ARGS.email])
        except(subprocess.CalledProcessError, IOError) as error_info:
            print(error_info)
            print(f'[WARN] Cannot delete {ARGS.email} from groups.')
            sys.exit(1)

    return True

def rename_user() -> str:
    """
    Renames the user to start with xx-

    Returns:
        str: New username with xx- suffix
    """
    if str.lower(ARGS.email).startswith('xx-'):
        return ARGS.email

    new_email = f'xx-{ARGS.email}'

    if ARGS.verbose:
        print(f'[INFO] Renaming {ARGS.email} to {new_email}')
    try:
        subprocess.check_call([GAM, 'update', 'user', ARGS.email, 'username', new_email])
    except(subprocess.CalledProcessError, IOError) as error_info:
        print(error_info)
        print(f'[CRITICAL] Cannot rename {ARGS.email}')
        sys.exit(1)

    time.sleep(2)
    return new_email

def remove_aliases(email_aliases: list) -> bool:
    """
    Remove email aliases from account

    Returns:
        bool: True if successful
    """
    if ARGS.verbose:
        print(f'[INFO] Removing aliases for account: {ARGS.email}')
    for cur_address in email_aliases:
        try:
            if ARGS.verbose:
                print(f'[INFO] Removing alias: {cur_address}')
            subprocess.check_call([GAM, 'delete', 'aliases', cur_address])
        except(subprocess.CalledProcessError, IOError) as error_info:
            if ARGS.email == cur_address:
                continue
            print(error_info)
            print(f'[WARN] Cannot delete aliases for {cur_address}')

    return True

def write_log(first_name: str, last_name: str, new_password: str, email_address: str) -> bool:
    """
    Write actions to log

    Args:
        first_name (str): User's first name
        last_name (str): user's last name
        new_password (str): password to account
        email_address: email address of user

    Returns:
        Bool: True if succesful

    """
    if ARGS.safe_log:
        new_password = '****'

    line = f'{first_name},{last_name},{email_address},{new_password}'

    with open(ARGS.log, 'a+', encoding='utf-8') as log_file:
        log_file.write(f'{line}\n')

    return True

def main():
    """
    This is the alpha and omega
    """

    print('[INFO] Starting offboarding process...')
    first_name, last_name, email_aliases, groups = get_user_info()
    while True:
        if ARGS.yes:
            break
        try:
            cont = str.lower(input('Do you want to continue offboarding (Y/N): '))
        except(TypeError, ValueError):
            pass
        except KeyboardInterrupt:
            print('[INFO] User aborted.')
            sys.exit(0)

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
    if not ARGS.nr:
        new_email = rename_user()
        email_aliases.append(ARGS.email)
    else:
        new_email = ARGS.email

    remove_aliases(email_aliases)

    if not ARGS.secure:
        print(f'{first_name},{last_name},{new_email},{new_password}')

    write_log(first_name, last_name, new_password, new_email)

    print('[INFO] Offboarding done.')
    sys.exit(0)

if __name__ == '__main__':
    main()
