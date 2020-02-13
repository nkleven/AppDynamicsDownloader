#!/usr/bin/python3

import requests
import json
import getpass
import sys


#  Obtain an OAuth Token from AppDynamics with your login and password
def get_token(username, password):
    creds = {"username": username,
             "password": password,
             "scopes": ["download"]}
    url = 'https://identity.msrv.saas.appdynamics.com/v2.0/oauth/token'
    r = requests.post(url, json=creds)
    j = json.loads(r.text)
    if 'error' not in j:
        print("Successfully obtained authentication token...")
        return j['access_token']
    if 'error' in j:
        print("Invalid credentials, please try again...")
        return 'failed'


# Grab the download URL for the pro
def get_url(selection, token):
    url = 'https://download.appdynamics.com/download/downloadfilelatest/'
    if selection == '1':
        print("Grabbing latest file list from AppDynamics...")
        r = requests.get(url)
        print("Importing list to process...")
        j = json.loads(r.text)
        for i in j:
            fn = i['filename']
            if 'platform-setup-x64-linux' in fn:
                confirm = input(fn +
                                '  is the latest version available, would you like to download it? (y/n): ')
                if confirm == 'y' or confirm == 'Y':
                    url = i['download_path']
                    download(url, fn, token)


def download(url, filename, token):
    with open(filename, 'wb') as f:
        header = {'Authorization': 'Bearer ' + token}
        response = requests.get(url, stream=True, headers=header)
        total = response.headers.get('content-length')

        if total is None:
            f.write(response.content)
        else:
            downloaded = 0
            total = int(total)
            for data in response.iter_content(chunk_size=max(int(total/1000), 1024*1024)):
                downloaded += len(data)
                f.write(data)
                done = int(50*downloaded/total)
                sys.stdout.write('\r[{}{}]'.format('█' * done, '.' * (50-done)))
                sys.stdout.flush()
    sys.stdout.write('\n')
    print("Download complete! Don't forget to make it executable!")


def main():
    username = input("Username: ")
    password = getpass.getpass(prompt='Password: ', stream=None)
    token = get_token(username, password)
    if token != 'failed':
        print("Please make a download selection")
        print("")
        print("1. Platform.x64.linux")
        print("")
        selection = input("Selection: ")
        if selection == "1":
            print('Selection Validated...')
            get_url('1', token)
        else:
            print('invalid selection')
    else:
        main()


main()
