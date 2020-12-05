#!/usr/bin/env python

#
# hacked up version of gam_offboarding to just change the user passwords
#

import argparse
import os
import sys
import random
import string
import time
import subprocess


PARSER = argparse.ArgumentParser(description='Logs user out and changes their password.')
PARSER.add_argument('email', help='User\'s address that will be changed.')
PARSER.add_argument('-v', '--verbose', action='stoee_true', help='Make this script talk a lot.')

ARGS = PARSER.parse_args()

HOME = os.path.expanduser("~")
GAM = os.path.join(HOME, '/bin/gamadv-xtd3/gam')


def get_random_password():
    length = 12
    letters = string.ascii_lowercase + string.ascii_uppercase
    password = ''
    while len(password) < length:
        if random.randint(0, 1):
            password += str(random.randint(0, 9))
            continue

        password += str(random.choice(letters))
        continue

    return password


def set_new_password(new_password):
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


def reset_tokens():
    if ARGS.verbose:
        print('[INFO] Resetting tokens for {}'.format(ARGS.email))
    try:
        subprocess.check_call([GAM, 'user', ARGS.email, 'deprovision'])
        subprocess.check_call([GAM, 'user', ARGS.email, 'update', 'backupcodes'])
    except(subprocess.CalledProcessError) as error_info:
        print(error_info)
        print('[CRITICAL] Failed deprovision/updating backup codes.')
        sys.exit(1)

    return True


def main():
    new_password = get_random_password()
    set_new_password(new_password)
    print('{} = {}'.format(args.EMAIL, new_password))
    reset_tokens()
    
    sys.exit(0)

if __name__ == '__main__':
    main()

