#!/usr/bin/env python3

import subprocess
import os
import argparse
import re

parser = argparse.ArgumentParser(description='GYB backups to xz')
parser.add_argument('path', type=str, help='path of archives')

args = parser.parse_args()

os.chdir(args.path)

archive_existing = []
archive_dirs = []
for val in os.listdir(args.path):
    if val.startswith('.'):
        continue
    if val.endswith('.tar.xz'):
        archive_existing.append(val)

    cur_path = os.path.join(args.path, val)
    if not os.path.isdir(cur_path):
        continue

    archive_dirs.append(val)

for cur_dir in archive_dirs:
    archive_name = re.sub(r'(?i)GYB-GMail-Backup-xx-', '', cur_dir)
    archive_name = re.sub(r'\.', '_', archive_name)
    archive_name = re.sub(r'@', '_', archive_name)
    archive_name = f'{archive_name}.tar.xz'
    if archive_name in archive_existing:
        continue

    dest_path = os.path.join(args.path, archive_name)
    cmd = f'tar -cJf - {cur_dir} | xz -9z -T0 > {dest_path}'
    print(cmd)
    subprocess.check_call(cmd, shell=True)

