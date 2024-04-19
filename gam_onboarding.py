#!/usr/bin/env python3

import argparse
import re
import subprocess
import sys
import datetime
import pytz
import random

GAM = ''

def new_val_cont(old_val, new_val):
    while True:
        try:
            cont = str.lower(input(f'{old_val} is ill-advised to use. We can replace it with: {new_val}\nDo you want to continue with the new {new_val}: '))
        except(TypeError, ValueError):
            continue

        if cont in ['yes', 'y']:
            return True
        if cont in ['no', 'n']:
            return False
    
def parse_args():
    parser = argparse.ArgumentParser(description='Onboard employee')
    parser.add_argument('first_name', type=str, help='Employee\'s first name')
    parser.add_argument('last_name', type=str, help='Employee\'s last name')
    parser.add_argument('personal_email', type=str, help='Email that credentials will be sent to.')
    parser.add_argument('city', type=str, choices=['chi', 'det', 'kc', 'la', 'ny', 'tky', 'none'], help='Location of employee')
    parser.add_argument('department', type=str, choices=['foo', 'foo1'], help='Department of employee')
    parser.add_argument('title', type=str, help='Offical postion/title of person')
    parser.add_argument('group', type=str, choices=['producer', 'editor', 'assistant', 'graphics', 'flame'], help='')
    parser.add_argument('type', type=str, choices=['freelance', 'staff'], help='Employee status is freelance or staff')

    args = parser.parse_args()
    
    return args

def get_random_password():
    length = 8
    chars = '!#$%&*0123456789<=>@ABCDEFGHIJKLMNOPQRSTUVWXYZ^_abcdefghijklmnopqrstuvwxyz'
    password = ''
    while len(password) < length:
        password += str(random.choice(chars))

    return password

def define_work_email_address(args):
    if re.search(r'^[A-Za-z]', args.first_name):
        new_first_name = re.sub(r'^[A-Za-z]', '', args.first_name)
        if new_val_cont(args.first_name, new_first_name):
            args.first_name = new_first_name
        
    if re.search(r'^[A-Za-z]', args.last_name):
        new_last_name = re.sub(r'^[A-Za-z]', '', args.last_name)
        if new_val_cont(args.last_name, new_last_name):
            args.last_name = new_last_name

    if args.department == 'foo':
        company = 'foo.com'
    elif args.department == 'foo1':
        company = 'foo1.com'
    else:
        company = 'foo.net'
    
    work_email = f'{args.first_name}.{args.last_name}@{company}'

    return work_email

def get_expire_date(args):
    exp_date =  datetime.datetime.now() + datetime.timedelta(days=2, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)

    local_tz = pytz.timezone('America/Chicago')
    if args.city in ['chi', 'kc', 'none']:
        dest_tz = pytz.timezone('America/Chicago')
    if args.city == 'det':
        dest_tz = pytz.timezone('America/Detroit')
    if args.city == 'la':
        dest_tz = pytz.timezone('America/Los_Angeles')
    if args.city == 'ny':
        dest_tz = pytz.timezone('America/New_York')
    if args.city == 'tky':
        dest_tz = pytz.timezone('Asia/Tokyo') 
    
    exp_date_localized = dest_tz.localize(exp_date)
    
    return exp_date_localized

def create_account(args, work_email):
    temp_password = get_random_password()

    try:
        subprocess.check_call([GAM, 'create', 'user', work_email, 'firstname', args.first_name, 'lastname', args.last_name, 'recoveryemail', args.personal_email, 'otheremail', 'home', args.personal_email, 'password', temp_password, 'changepassword', 'on', 'notify', args.personal_email])
    except(subprocess.CalledProcessError, IOError) as error_info:
        print(error_info)
        return False

    return True

def set_groups(args, work_email):
    if args.city == 'chi':
        city = 'chicago'
    elif args.city == 'det':
        city = 'detroit'
    elif args.city == 'kc':
        city = 'kc'
    elif args.city == 'la':
        city = 'la'
    elif args.city == 'ny':
        city = 'ny'
    elif args.city == 'tky':
        city = 'tokyo'
    else:
        return True
    
    company = work_email.split('@')[1]
    
    group_email = f'{city}@{company}'
    try:
        subprocess.check_call([GAM, 'update', 'group', group_email, 'add'])
    except(subprocess.CalledProcessError, IOError) as error_info:
        print(error_info)
        print(f'[ERROR] Cannot add {work_email} to {group_email}')

    if args.type == 'staff':
        group_email = f'{city}.staff@foo.net'
        try:
            subprocess.check_call([GAM, 'update', 'group', group_email])
        except(subprocess.CalledProcessError, IOError) as error_info:
            print(error_info)
            print(f'[ERROR] Cannot add {work_email} to {group_email}')
    
    if args.department == 'dictionary':
        try:
            subprocess.check_call([GAM, 'update', 'group', 'chicago.prep@dictionaryfilms.com'])
        except(subprocess.CalledProcessError, IOError) as error_info:
            print(error_info)
            print(f'[ERROR] Cannot add {work_email} to chicago.prep@dictionaryfilms.com')

    if args.group == 'producer':
        group_email = f'{city}.producers@{company}'
        try:
            subprocess.check_call([GAM, 'update', 'group', group_email])
        except(subprocess.CalledProcessError, IOError) as error_info:
            print(error_info)
            print(f'[ERROR] Cannot add {work_email} to {group_email}')

    if args.group == 'editor':
        group_email = f'{city}.editors@{company}'
        try:
            subprocess.check_call([GAM, 'update', 'group', group_email])
        except(subprocess.CalledProcessError, IOError) as error_info:
            print(error_info)
            print(f'[ERROR] Cannot add {work_email} to {group_email}')

    if args.group == 'flame':
        group_email = f'{city}.flame@{company}'
        try:
            subprocess.check_call([GAM, 'update', 'group', group_email])
        except(subprocess.CalledProcessError, IOError) as error_info:
            print(error_info)
            print(f'[ERROR] Cannot add {work_email} to {group_email}')

    if args.group == 'assistant':
        group_email = f'{city}.assistants@{company}'
        try:
            subprocess.check_call([GAM, 'update', 'group', group_email])
        except(subprocess.CalledProcessError, IOError) as error_info:
            print(error_info)
            print(f'[ERROR] Cannot add {work_email} to {group_email}')

    return True

def set_ou(args):
    return True

def set_signature(args, work_email):
    return True

def email_creds():
    return True

def main():
    args = parse_args()
    work_email = define_work_email_address(args)

    if not create_account(args, work_email):
        return 2
    if not set_groups(args, work_email):
        return 3
    if not set_ou(args):
        return 4
    if not set_signature(args, work_email):
        return 5
    if not email_creds():
        return 6

    return 0

if __name__ == '__main__':
    error_code = main()
    sys.exit(error_code)
