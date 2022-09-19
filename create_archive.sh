#!/bin/sh

email=$1

# if no email address is provided or if -h is used, print usage
if [ -z "$email" ] || [ "$email" = "-h" ] || [ "$email" = "--help" ]; then
    echo "Usage: $0 email_address"
    exit 1
fi

mkdir -pv -m 755 /media/tmp_mail/${email}/email /media/tmp_mail/${email}/chat
