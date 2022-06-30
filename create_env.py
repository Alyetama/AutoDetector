#!/usr/bin/env python
# coding: utf-8

import os
import random
import secrets
import string
import sys


def generate_password(length=12):
    safe_symbols = '+-.@^_'
    chars = string.ascii_letters + string.digits + safe_symbols
    chars = list(chars * random.randint(10, 1000))
    random.shuffle(chars)
    while True:
        password = [secrets.choice(chars) for _ in range(length)]
        random.shuffle(password)
        password = ''.join(password)
        if (any(c.islower() for c in password) and any(c.isupper()
                                                       for c in password)
                and sum(c.isdigit() for c in password) >= 3
                and sum(c in safe_symbols for c in password) >= 1):
            return password


USER_EMAIL_ADDRESS = input('Enter your email address then hit ENTER:\n'
                           '> ')
confirm_email_address = input('Confirm your email address then hit ENTER:\n'
                              '> ')
if USER_EMAIL_ADDRESS != confirm_email_address:
    print('Email addresses do not match. Please try again.')
    sys.exit(1)

if os.getenv('TAILSCALE_IP'):
    LOCAL_ADDRESS = os.getenv('TAILSCALE_IP')
else:
    LOCAL_ADDRESS = '127.0.0.1'

with open('.env', 'w') as f:
    f.write('MINIO_ROOT_USER=admin\n')
    f.write(f'MINIO_ROOT_PASSWORD={generate_password()}\n')
    f.write(f'MINIO_DOMAIN={LOCAL_ADDRESS}:9000\n')
    f.write(f'MINIO_SERVER_URL=http://{LOCAL_ADDRESS}:9000\n')
    f.write(f'MINIO_BROWSER_REDIRECT_URL=http://{LOCAL_ADDRESS}:9001\n\n')

    f.write(f'LABEL_STUDIO_HOST=http://{LOCAL_ADDRESS}:8080\n')
    f.write(f'LABEL_STUDIO_PORT=8080\n')
    f.write(f'LABEL_STUDIO_USERNAME={USER_EMAIL_ADDRESS}\n')
    f.write(f'LABEL_STUDIO_PASSWORD={generate_password()}\n\n')

    f.write(f'POSTGRE_HOST={LOCAL_ADDRESS}\n')
    f.write(f'POSTGRE_PORT=5432\n')
    f.write(f'POSTGRE_NAME=postgres\n')
    f.write(f'POSTGRE_USER=postgres\n')
    f.write(f'POSTGRE_PASSWORD={generate_password()}\n\n')
