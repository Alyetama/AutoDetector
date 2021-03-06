#!/usr/bin/env python
# coding: utf-8

import os
import secrets
import socket
from pathlib import Path


def generate_passphrase(length=4):
    if not Path('/usr/share/dict/words').exists():
        words_file = 'words'
    else:
        words_file = '/usr/share/dict/words'
    with open(words_file) as f:
        words = [word.strip() for word in f]
        passphrase = '-'.join(secrets.choice(words) for i in range(length))
        return passphrase


if not os.getenv('USER_EMAIL_ADDRESS'):
    os.environ['USER_EMAIL_ADDRESS'] = input('Email address: ')

USER_EMAIL_ADDRESS = os.environ['USER_EMAIL_ADDRESS']

if os.getenv('TAILSCALE_IP'):
    LOCAL_ADDRESS = os.getenv('TAILSCALE_IP')
else:
    S3_ENDPOINT = os.popen(
        'ifconfig | grep "inet " | grep -Fv 127.0.0.1 | awk \'{print $2}\' | head -1'  # noqa: E501
    ).read().strip()
    if not S3_ENDPOINT:
        S3_ENDPOINT = socket.gethostbyname(socket.gethostname())
    LOCAL_ADDRESS = '127.0.0.1'

with open('.env', 'w') as f:
    f.write('S3_ROOT_USER=admin\n')
    f.write(f'S3_ROOT_PASSWORD={generate_passphrase()}\n')
    f.write(f'S3_DOMAIN={LOCAL_ADDRESS}:9000\n')
    f.write(f'S3_SERVER_PORT=9000\n')
    f.write(f'S3_CONSOLE_PORT=9001\n')
    f.write(f'S3_SERVER_URL=http://{S3_ENDPOINT}:9000\n')
    f.write(f'S3_BROWSER_REDIRECT_URL=http://{LOCAL_ADDRESS}:9001\n\n')
    f.write(f'S3_ENDPOINT=http://{S3_ENDPOINT}:9000\n\n')

    f.write(f'LABEL_STUDIO_HOST=http://{LOCAL_ADDRESS}:8080\n')
    f.write(f'LABEL_STUDIO_PORT=8080\n')
    f.write(f'LABEL_STUDIO_USERNAME={USER_EMAIL_ADDRESS}\n')
    f.write(f'LABEL_STUDIO_PASSWORD={generate_passphrase()}\n\n')

    f.write(f'POSTGRES_HOST={LOCAL_ADDRESS}\n')
    f.write(f'POSTGRES_PORT=5432\n')
    f.write(f'POSTGRES_NAME=postgres\n')
    f.write(f'POSTGRES_USER=postgres\n')
    f.write(f'POSTGRES_PASSWORD={generate_passphrase()}\n\n')
