#!/usr/bin/env python

#
# reads csv formatted as email,access (needs header to match) to set proper group permissions.
# access set as internal can be messaged by only people within the domain.
# access set as external can be messaged by anyone.
#
#
# Note: Google states there is a 100,000 API limit per day. This script runs 30 calls per group.
# If needed you can request more: https://developers.google.com/admin-sdk/groups-settings/limits
#

import csv
import subprocess
import time
import sys
import os
import multiprocessing

HOME = os.path.expanduser("~")
GAM = os.path.join(HOME, 'bin/gamadv-xtd3/gam')

if not os.path.exists(GAM):
    print('[FATAL] GAM is not installed here: {}'.format(GAM))

ATTEMPT_COOL_DOWN = 5  # seconds
ATTEMPT_LIMIT = 10  # seconds
COOL_DOWN_GROWTH = 2  # rate

CONCURRENT_PROCESSES = 5 # concurrent group processes run. I would not go above 10.

def get_group_names():
    with open (sys.argv[1], 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            yield row['email'], row['access']

def gam_cmd(group_vars):
    group_name = group_vars[0]
    access = group_vars[1]

    print('[INFO] Changing group ACLs for {} as an {} group... this takes approximately 2-5 minutes per group.'.format(group_name, access))
    sleep_time = ATTEMPT_COOL_DOWN
    attempts = 0
    FNULL = open(os.devnull, 'w')
    start_time = time.time()
    while True:
        try:
            subprocess.check_call([GAM, 'update', 'group', group_name, 'allowExternalMembers', 'true'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'allowWebPosting', 'false'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'archive_only', 'false'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'customRolesEnabledForSettingsToBeMerged', 'false'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'enableCollaborativeInbox', 'false'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'includeCustomFooter', 'false'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'includeInGlobalAddressList', 'true'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'is_archived', 'false'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'membersCanPostAsTheGroup', 'false'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'messageModerationLevel', 'MODERATE_NONE'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'replyTo', 'REPLY_TO_IGNORE'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'sendMessageDenyNotification', 'true'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'spamModerationLevel', 'allow'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'who_can_join', 'invited_can_join'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'who_can_invite', 'none_can_invite'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'who_can_leave_group', 'none_can_leave'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'who_can_view_group', 'all_managers_can_view'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'who_can_view_membership', 'all_managers_can_view'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'whoCanDiscoverGroup', 'ALL_IN_DOMAIN_CAN_DISCOVER'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'show_in_group_directory', 'true'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'whoCanAssistContent', 'NONE'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'whoCanModerateContent', 'OWNERS_AND_MANAGERS'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'whoCanModerateMembers', 'OWNERS_ONLY'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'allow_google_communication', 'false'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'favoriteRepliesOnTop', 'true'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'messageDisplayFont', 'DEFAULT_FONT'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'whoCanAddReferences', 'NONE'], stdout=FNULL, stderr=subprocess.STDOUT)
            subprocess.check_call([GAM, 'update', 'group', group_name, 'whoCanMarkFavoriteReplyOnOwnTopic', 'NONE'], stdout=FNULL, stderr=subprocess.STDOUT)
            
            if access == 'internal':
                subprocess.check_call([GAM, 'update', 'group', group_name, 'who_can_post_message', 'allindomaincanpost'], stdout=FNULL, stderr=subprocess.STDOUT)
                subprocess.check_call([GAM, 'update', 'group', group_name, 'whoCanContactOwner', 'allindomaincancontact'], stdout=FNULL, stderr=subprocess.STDOUT)
            if access == 'external':
                subprocess.check_call([GAM, 'update', 'group', group_name, 'who_can_post_message', 'anyone_can_post'], stdout=FNULL, stderr=subprocess.STDOUT)
                subprocess.check_call([GAM, 'update', 'group', group_name, 'whoCanContactOwner', 'anyone_can_contact'], stdout=FNULL, stderr=subprocess.STDOUT)
            
            end_time = time.time()
            delta_time = int(end_time) - int(start_time)
            print('[INFO] {} complete in {} seconds.'.format(group_name, delta_time))
            break

        except(subprocess.CalledProcessError, IOError) as error_info:
            print(error_info)
            attempts += 1
            if attempts >= ATTEMPT_LIMIT:
                print('[FATAL] Too many attempt to changing this group, moving on.')
                return

            print('[WARN] Error running group acl... waiting {} seconds to try again.'.format(sleep_time))
            time.sleep(sleep_time)
            sleep_time *= COOL_DOWN_GROWTH
    
    return

def main():
    pool = multiprocessing.Pool(processes=CONCURRENT_PROCESSES)
    all_groups = []
    for group_name, access in get_group_names():
        all_groups.append((group_name, access))
        
    pool.map(gam_cmd, all_groups)
    return

main()
print('[INFO] All done!')
sys.exit(0)
