#!/usr/bin/env python3

import argparse
import re
import os
import subprocess

HOME = os.path.expanduser("~")
GAM = os.path.join(HOME, 'bin/gamadv-xtd3/gam')
DEFAULT_LOG_PATH = os.path.join(HOME, 'Desktop')

PARSER = argparse.ArgumentParser(description='Find contributors of a document from a file id.')
PARSER.add_argument('id', help='Google Drive ID to search')
PARSER.add_argument('log', nargs='?', type=str, help=f'Specify log directory. Default: {DEFAULT_LOG_PATH}')
PARSER.add_argument('-v', '--verbose', action='store_true', help='For people that like it nerdy.')

ARGS = PARSER.parse_args()

if ARGS.log:
    ARGS.log = os.path.join(ARGS.log, f'{ARGS.id}.log')
else:
    ARGS.log = os.path.join(DEFAULT_LOG_PATH, f'{ARGS.id}.log')

usr_output = subprocess.Popen([GAM, 'print', 'users'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf8')
usr_output = usr_output.communicate()[0]

print('[INFO] Searching...')
with open(ARGS.log, 'w') as log_file:
    for output_line in usr_output.splitlines():
        output_line = output_line.lstrip()
        output_line = output_line.rstrip()
        if not re.search(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', output_line):
            continue

        file_output = subprocess.Popen([GAM, 'user', output_line, 'show', 'fileinfo', ARGS.id], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf8')
        file_output = file_output.communicate()[0]

        found_user = True
        for file_line in file_output.splitlines():
            if re.search(r'(?i)Show Failed\: Does not exist', file_line):
                found_user = False
                break
        
        if found_user:
            csv_line = f'{output_line},yes'
        else:
            csv_line = f'{output_line},no'
        
        log_file.write(f'{csv_line}\n')
        if ARGS.verbose:
            print(csv_line)
