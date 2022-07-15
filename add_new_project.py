#!/usr/bin/env python
# coding: utf-8

# import ipaddress

import json
import os
import random
import string
import time
from typing import Optional, Union

import requests
from dotenv import load_dotenv
from requests.structures import CaseInsensitiveDict


def api_request(url: str,
                method: str = 'get',
                data: Optional[dict] = None) -> Union[dict, list, str]:
    """Makes an API request to the given url with the given method and data.

    Args:
        url (str): The url to make the request to.
        method (str): The HTTP method to use. Defaults to 'get'.
        data (Optional[dict]): The data to send with the request. Defaults to
            None.

    Returns:
        The response from the API.

    """
    load_dotenv()
    headers = CaseInsensitiveDict()
    headers['Content-type'] = 'application/json'
    headers['Authorization'] = f'Token {os.environ["LABEL_STUDIO_TOKEN"]}'
    if method.lower() == 'post':
        response = requests.post(url, headers=headers,
                                 data=json.dumps(data)).json()
    elif method.lower() == 'get':
        response = requests.get(url, headers=headers).json()
    return response


def add_new_project() -> Optional[dict]:
    """Creates a new project in Label Studio.

    Returns:
        dict: The new project's metadata.

    Raises:
        ValueError: If the project already exists.

    """
    allowed = string.ascii_letters + string.digits + '_-'
    print('Note: The project name should have no spaces or special '
          'characters (except "-" or "_").')

    while True:
        new_project_folder_name = input('Pick a project name: ').replace(
            ' ', '_')
        if len(new_project_folder_name) < 3:
            print(
                '\033[91mProject name must be at least 3 characters long.\033[0m\n'  # noqa: E501
            )
            continue
        elif any(c for c in new_project_folder_name if c not in allowed):
            print('\033[91mInvalid project name! Special characters, '
                  'except "-" and "_", are not allowed!\033[0m')
        else:
            break

    print('-' * 80)

    view = '''<View>
      <Image name="image" value="$image"/>
      <RectangleLabels name="label" toName="image">
        <Label value="Background" background="blue"/>
        </RectangleLabels>
    </View>'''

    color = random.choice(
        ['#ff5555', '#8be9fd', '#50fa7b', '#ffb86c', '#ff79c6'])
    template = {
        'title': new_project_folder_name,
        'color': color,
        'label_config': view
    }

    response = api_request(f'{LABEL_STUDIO_HOST}/api/projects',
                           method='post',
                           data=template)

    print('\n\nStep 1:')
    print(
        '    - Visit the URL below to add labels (1 label per line), '
        'then click on `Add` -> `Save`:\n'
        f'    {LABEL_STUDIO_HOST}/projects/{response["id"]}/settings/labeling'
        '\n\n')  # noqa: E501
    time.sleep(3)
    os.popen(
        f'open {LABEL_STUDIO_HOST}/projects/{response["id"]}/settings/labeling'
    )

    while True:
        done_resp = input('Done (yes/no)? ')
        if done_resp.lower() in ['yes', 'y']:
            break
    return response


def add_data_storage(project_response: dict,
                     bucket_name: str = 'images',
                     prefix: Optional[str] = None) -> dict:
    """Add the new project to label-studio, then sync its local data.

    Args:
        project_response (dict): The response from the `create project` API.
        bucket_name (str): The name of the bucket to sync the data to (defaults
            to 'images').
        prefix (str): The prefix to add to the bucket name (defaults to '').

    Returns:
        dict: The response from the API request.

    """
    p_title = project_response['title']

    print('\nStep 2:')
    print('    - Visit the URL below to upload your image files. Simply '
          'click on the "upload" button to upload your files.')
    time.sleep(1)
    print(f'{os.environ["S3_SERVER_URL"]}/buckets/images/browse')
    os.popen(
        f'open {os.environ["S3_BROWSER_REDIRECT_URL"]}/buckets/images/browse')

    if 'http://' not in os.environ['S3_ENDPOINT']:
        os.environ['S3_ENDPOINT'] = f'http://{os.environ["S3_ENDPOINT"]}'

    storage_dict = {
        "type": "s3",
        "presign": True,
        "title": p_title,
        "bucket": bucket_name,
        "prefix": prefix,
        "use_blob_urls": True,
        "aws_access_key_id": os.environ['S3_ACCESS_KEY'],
        "aws_secret_access_key": os.environ['S3_SECRET_KEY'],
        "region_name": 'us-east-1',
        "s3_endpoint": os.environ['S3_ENDPOINT'],
        "recursive_scan": True,
        "project": project_response['id']
    }
    storage_request = {
        'url': f'{LABEL_STUDIO_HOST}/api/storages/s3',
        'method': 'post',
        'data': storage_dict
    }

    storage_response = api_request(**storage_request)
    print(storage_response)

    while True:
        done_resp = input('Done (yes/no)? ')
        if done_resp.lower() in ['yes', 'y']:
            break

    print(
        '\nStep 3:\n'
        '    - After uploading your images, visit the URL below, '
        'then click on `Sync Storage`:\n'
        f'    {LABEL_STUDIO_HOST}/projects/{project_response["id"]}/settings/storage\n'  # noqa: E501
    )
    time.sleep(1)
    os.popen(
        f'open {LABEL_STUDIO_HOST}/projects/{project_response["id"]}/settings/storage'  # noqa: E501
    )
    return storage_response


if __name__ == '__main__':
    load_dotenv()
    LABEL_STUDIO_HOST = os.environ['LABEL_STUDIO_HOST']
    # try:
    #     if ipaddress.ip_address(
    #             os.environ['LABEL_STUDIO_HOST'].split('/')[-1]):
    #         LABEL_STUDIO_HOST = f'{os.environ["LABEL_STUDIO_HOST"]}:{os.environ["LABEL_STUDIO_PORT"]}'  # noqa: E501
    # except ValueError:
    #     pass
    new_project = add_new_project()
    add_data_storage(new_project)
