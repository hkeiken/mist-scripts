#!/usr/bin/env python3
'''
Author: Hans Kristian Eiken, hans@eikjen.no

Script to add and delete pre-shared keys in bulk at a Mist site.
Use-case is a hotel with want for a psk-per room with a dedicated
vlanper room. This means the same vlan must be configured at the
Mist access point ethernet port.

Dependent of a token saved in a file named "token",
containing only the token on a single line.

Usage for adding psk: ./psk-mgmt-bulk.py add site_id csv_file
Usage for deleting psk: ./psk-mgmt.py delete site_id csv_file

Example csv_file:
id;key;ssid;password;vlan
1;room101;skurva_hotell;1234;30
2;room102;skurva_hotell;1000;31

Example use:

Add:
Adds key;ssid;password and vlan:

Delete uses the same csv_file, but only the key field is used for deletion:

This is not a production ready script, but a proof of
capabilities quickly thrown together.
'''

import os
import sys
import re
import json
import csv
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

def read_csv_file(csv_file_name):
    '''
    Function to read a csv file of sites
     contain id;key;ssid;password;vlan
     id - id for row
     key - name of key, only used internally in Mist to identify key
     ssid - ssid the key should be used in
     password - password for accessing keys
     vlan - vlan assigned to key
    '''
    try:
        if os.path.isfile(csv_file_name):
            with open(csv_file_name, mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file,delimiter=';')
                line_count = 0
                key_list = []
                for row in csv_reader:
                    key_list.append({'key': row['key'],'ssid' :row['ssid'],'password' :row['password'], 'vlan' :row['vlan']})
            return key_list #Returned site_list dictionary
    except OSError:
        return []


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
        return_text = 'PSK {} created at site "{}" successfully'.format(key_name,site_name )+"\n"
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
        return_text = 'Sucessfully deleted PSK {} at site "{}"'.format(key_name,site_name)+"\n"
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
    key_list = read_csv_file(csv_file)

    #Validate site_id:
    if validate_mist_id(sys.argv[2]):
        #Reading attributes add site_id key_name ssid vlan password
        if len(sys.argv) == 3+1 and sys.argv[1] == 'add':
            return_text = ''
            for key in key_list:
                return_text += mist_add_psk(mist_url,headers,site_id,key['key'],key['ssid'],key['vlan'],key['password'])
        #Reading attributes delete site_id key_name
        elif len(sys.argv) == 3+1 and sys.argv[1] == 'delete':
            return_text = ''
            for key in key_list:
                return_text += mist_delete_psk(mist_url,headers,site_id,key['key'])
        else:
            return_text = "Wrong action or number of arguments."
    else:
        return_text = "Wrong site-id size."
    print(return_text)

if __name__ == '__main__':
    #Reading attributes
    if len(sys.argv) == 3+1:
        csv_file = sys.argv[3]
        if validate_mist_id(sys.argv[2]):
                site_id = sys.argv[2]
        else:
            site_id =''
        main()
    else:
        print("Wrong number of arguments")
