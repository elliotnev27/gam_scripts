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

ATTEMPT_COOL_DOWN = 5  # seconds
ATTEMPT_LIMIT = 10  # seconds
COOL_DOWN_GROWTH = 2  # rate


def get_group_names():
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

    return group_list


def gam_cmd(group_name):
    print('[INFO] Changing group ACL for {}'.format(group_name))
    try:
        subprocess.check_call([GAM, 'update', 'group', group_name, 'show_in_group_directory', 'true'])
        subprocess.check_call([GAM, 'update', 'group', group_name, 'who_can_invite', 'none_can_invite'])
        subprocess.check_call([GAM, 'update', 'group', group_name, 'who_can_join', 'invited_can_join'])
        subprocess.check_call([GAM, 'update', 'group', group_name, 'who_can_post_message', 'anyone_can_post'])
        subprocess.check_call([GAM, 'update', 'group', group_name, 'who_can_view_group', 'all_managers_can_view'])
        subprocess.check_call([GAM, 'update', 'group', group_name, 'who_can_view_membership', 'all_managers_can_view'])
        subprocess.check_call([GAM, 'update', 'group', group_name, 'allow_google_communication', 'false'])
        subprocess.check_call([GAM, 'update', 'group', group_name, 'allow_web_posting', 'false'])
        subprocess.check_call([GAM, 'update', 'group', group_name, 'archive_only', 'false'])
        subprocess.check_call([GAM, 'update', 'group', group_name, 'is_archived', 'false'])
        subprocess.check_call([GAM, 'update', 'group', group_name, 'members_can_post_as_the_group', 'false'])
        subprocess.check_call([GAM, 'update', 'group', group_name, 'spamModerationLevel', 'allow'])
        subprocess.check_call([GAM, 'update', 'group', group_name, 'include_in_global_address_list', 'true'])
        subprocess.check_call([GAM, 'update', 'group', group_name, 'who_can_leave_group', 'none_can_leave'])
        subprocess.check_call([GAM, 'update', 'group', group_name, 'who_can_contact_owner', 'ANYONE_CAN_CONTACT'])
    except(subprocess.CalledProcessError, IOError) as error_info:
        return False

    return True


def main():
    group_list = get_group_names()
    for group_name in group_list:
        sleep_time = ATTEMPT_COOL_DOWN
        attempts = 0
        while True:
            if gam_cmd(group_name):
                break

            attempts += 1
            if attempts >= ATTEMPT_LIMIT:
                print('[FATAL] Too many attempt to changing this group, moving on.')
                break

            print('[WARN] Error running group acl... waiting {} seconds to try again.'.format(sleep_time))
            time.sleep(sleep_time)
            sleep_time *= COOL_DOWN_GROWTH


main()
print('[INFO] All done!')
sys.exit(0)
