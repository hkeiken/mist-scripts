#!/usr/bin/env python3
'''
Author: Hans Kristian Eiken, hans@eikjen.no

Script to add and delete pre-shared keys at a Mist site. Use-case
is a hotel with want for a psk-per room with a dedicated vlan
per room. This means the same vlan must be configured at the
Mist access point ethernet port.

Dependent of a token saved in a file named "token",
containing only the token on a single line.

Usage for adding psk: ./psk-mgmt.py add site_id key_name ssid vlan-id password
Usage for deleting psk: ./psk-mgmt.py delete site_id key_name
Usage for showing psk: ./psk-mgmt.py show site_id key_name

Examples:
./psk-mgmt.py add 18bf02e3-0000-0000-0000-7a5284471c4f rom100 skurva-hotell 123 1234
PSK rom100 created at site "Osloveien 1" successfully

./psk-mgmt.py delete 18bf02e3-0000-0000-0000-7a5284471c4f test1
Sucessfully deleted PSK test1 at site "Osloveien 1"

./psk-mgmt.py show 18bf02e3-0000-0000-0000-7a5284471c4f rom100
Site name: Osloveien 1
Site id:   18bf02e3-0000-0000-0000-7a5284471c4f
Key name:  rom100
SSID:      skurva-hotell
Vlan id:   123
Password:  1234

./psk-mgmt.py update 18bf02e3-0000-0000-0000-7a5284471c4f rom100 test2
Updated key rom100 with new password
 
This is not a production ready script, but a proof of
capabilities quickly thrown together.
'''

import os
import sys
import re
import json
import requests

def read_tokenfile(tokenfile):
    '''
    Function to read a file tokenfile. This file contains
    only the API token for accessing Mist API
    '''
    try:
        if os.path.isfile(tokenfile):
            file = open(tokenfile, "r")
            token = str(file.readline().strip())
            file.close()
            if len(token) == 96:
                return token
            else:
                return ''
    except OSError:
        return ''

def is_allowed_specific_char(string):
    '''
    Function checking for valid letters
    '''
    charRe = re.compile(r'[^a-f0-9-]')
    string = charRe.search(string)
    return not bool(string)

def validate_mist_id(id):
    '''
    Function to validate Mist id for length and characters
    '''
    if (len(id) == 36 and is_allowed_specific_char(id)):
        return True
    else:
        return False

def get_device_organization(mist_url,headers,site_id,device_id):
    '''
    Function to get organization id based on device id
    '''
    api_url = '{}sites/{}/devices?type=switch'.format(mist_url,site_id)
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        devices = json.loads(response.content.decode('utf-8'))
        org_id =''
        for device in devices:
            if device['id'] == device_id:
                org_id = device['org_id']
    return org_id


def get_last_device_at_site(mist_url,headers,site_id):
    '''
    Function to get last device id at site (reused to get org)
    '''
    api_url = '{}sites/{}/devices?type=switch'.format(mist_url,site_id)
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        devices = json.loads(response.content.decode('utf-8'))
        device_id =''
        for device in devices:
            device_id = device['id']
    return device_id


def get_site_name(mist_url,headers,site_id):
    '''
    Function to extract site_name from site_id. Needs at least one device at site.
    '''
    last_device_id =  get_last_device_at_site(mist_url,headers,site_id)
    org_id = get_device_organization(mist_url,headers,site_id,last_device_id)
    api_url = '{}orgs/{}/sites'.format(mist_url,org_id,site_id)
    response = requests.get(api_url, headers=headers)
    this_site=''
    if response.status_code == 200:
        sites = json.loads(response.content.decode('utf-8'))
        for site in sites:
            if site['id'] == site_id:
                this_site = site['name']
    return this_site

def mist_add_psk(mist_url,headers,site_id,key_name,ssid,vlan,password):
    '''
    Function for adding PSK to Mist site
    '''
    return_text = ''
    api_url = '{}sites/{}/psks'.format(mist_url,site_id)
    psk_info = { "name": key_name,
        "passphrase": password,
        "ssid": ssid,
        "usage": 'multi',
        "vlan_id": vlan
        }
    site_name = get_site_name(mist_url,headers,site_id)
    response = requests.post(api_url, json=psk_info, headers=headers)
    if response.status_code != 200:
        return_text = 'Failure creating PSK.'
    else:
        output = json.loads(response.content.decode('utf-8'))
        return_text = 'PSK {} created at site "{}" successfully'.format(key_name,site_name )
    return return_text

def mist_delete_psk(mist_url,headers,site_id,key_name):
    '''
    Function for adding PSK to Mist site
    '''
    return_text = ''
    api_url = '{}sites/{}/psks?name={}'.format(mist_url,site_id,key_name)
    response = requests.delete(api_url, headers=headers)
    site_name = get_site_name(mist_url,headers,site_id)
    if response.status_code == 200:
        psk = json.loads(response.content.decode('utf-8'))
        return_text = 'Sucessfully deleted PSK {} at site "{}"'.format(key_name,site_name)
    return return_text

def mist_show_psk(mist_url,headers,site_id,key_name):
    '''
    Function for showing PSK to Mist site
    '''
    return_text = ''
    api_url = '{}sites/{}/psks?name={}'.format(mist_url,site_id,key_name)
    response = requests.get(api_url, headers=headers)
    site_name = get_site_name(mist_url,headers,site_id)
    if response.status_code == 200:
        psk = json.loads(response.content.decode('utf-8'))
        return_text =  "Site name: {}\n".format(site_name)
        return_text += "Site id:   {}\n".format(site_id)
        return_text += "Key name:  {}\n".format(key_name)
        return_text += "SSID:      {}\n".format(psk[0]['ssid'])
        return_text += "Vlan id:   {}\n".format(psk[0]['vlan_id'])
        return_text += "Password:  {}".format(psk[0]['passphrase'])
    else:
        return_text = 'Could not find PSK: {}'.format(key_name)
    return return_text

def mist_update_psk(mist_url,headers,site_id,key_name,password):
    '''
    Function for showing PSK to Mist site
    '''
    return_text = ''
    api_url = '{}sites/{}/psks?name={}'.format(mist_url,site_id,key_name)
    response = requests.get(api_url, headers=headers)
    site_name = get_site_name(mist_url,headers,site_id)
    if response.status_code == 200:
        psk = json.loads(response.content.decode('utf-8'))
        ssid=psk[0]['ssid']
        vlan_id = psk[0]['vlan_id']
        mist_add_psk(mist_url,headers,site_id,key_name,ssid,vlan_id,password)
        return_text = 'Updated key {} with new password'.format(key_name)
    else:
        return_text = 'Could not find PSK: {}'.format(key_name)
    return return_text

def main():
    '''
    Main function
    '''
    return_text = ''
    token = read_tokenfile('token')
    mist_url = 'https://api.mist.com/api/v1/'
    headers = {'Content-Type': 'application/json',
             'Authorization': 'Token {}'.format(token)}
    #Validate site_id:
    if validate_mist_id(sys.argv[2]):
        #Reading attributes add site_id key_name ssid vlan password
        if len(sys.argv) == 6+1 and sys.argv[1] == 'add':
            site_id = sys.argv[2]
            key_name = sys.argv[3]
            ssid = sys.argv[4]
            vlan = sys.argv[5]
            password = sys.argv[6]
            return_text = mist_add_psk(mist_url,headers,site_id,key_name,ssid,vlan,password)
        #Reading attributes delete site_id key_name
        elif len(sys.argv) == 3+1 and sys.argv[1] == 'delete':
            site_id = sys.argv[2]
            key_name = sys.argv[3]
            return_text = mist_delete_psk(mist_url,headers,site_id,key_name)
        #Reading attributes show site_id key_name
        elif len(sys.argv) == 3+1 and sys.argv[1] == 'show':
            site_id = sys.argv[2]
            key_name = sys.argv[3]
            return_text = mist_show_psk(mist_url,headers,site_id,key_name)
        #Reading attributes update site_id key_name
        elif len(sys.argv) == 4+1 and sys.argv[1] == 'update':
            site_id = sys.argv[2]
            key_name = sys.argv[3]
            password = sys.argv[4]
            return_text = mist_update_psk(mist_url,headers,site_id,key_name,password)
        else:
            return_text = "Wrong action or number of arguments."
    else:
        return_text = "Wrong site-id size."
    print(return_text)

if __name__ == '__main__':
    main()
