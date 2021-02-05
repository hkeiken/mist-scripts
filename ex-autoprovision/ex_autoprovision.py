#!/usr/bin/env python3
'''
Author: Hans Kristian Eiken, hans@eikjen.no

Script to autoprovision Juniper EX switches when they
show up at a staging site to a new site based on list attached.

Dependent of a token saved in a file named "token",
containing only the token on a single line.

Usage for site info: ./ex_autoprovision.py site_list.csv staging_site_id

This is not a production ready script, but a proof of
capabilities quickly thrown together.
'''

import os
import json
import requests
import sys
import csv
import re
from netaddr import IPNetwork, IPAddress

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
     contain id;Network;Site-id;Eventually;More;Columns
     id - id for row
     network - network for management network id
     site-id - Mist id for site
       more can be one or more field for humans, typically site name
       or other information. The script only uses the two first
       columns.
    '''
    try:
        if os.path.isfile(csv_file_name):
            with open(csv_file_name, mode='r') as csv_file:
                csv_reader = csv.DictReader(csv_file,delimiter=';')
                line_count = 0
                site_list = []
                for row in csv_reader:
                    site_list.append({'network': row['network'],'site-id' :row['site-id']})
            return site_list #Returned site_list dictionary
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
    Function to validate Mist id
    '''
    if (len(id) == 36 and is_allowed_specific_char(id)):
        return True
    else:
        return False

def get_device_stat_info(device_stat_info,type):
    '''
    Function to extract specific info out of device stats info set
    '''
    if isinstance(device_stat_info[type],str):
        return_text = device_stat_info[type]
    else:
        return_text = "Error, no info"
    return return_text

def get_switch_stat_info(mist_url,headers,site_id,device_id):
    '''
    Function to get stat info for a switch switch
    '''
    api_url = '{0}sites/{1}/stats/devices?type=switch'.format(mist_url,site_id)
    #print(api_url)
    response = requests.get(api_url, headers=headers)
    return_bol = False
    device_stat_info = ''
    if response.status_code == 200:
        devices = json.loads(response.content.decode('utf-8'))
        for device in devices:
            device_stat_info = device
            return_bol = True
    else:
        print("Error Fetching switch stat")
    return return_bol,device_stat_info

def check_site_for_connected_switches(mist_url,headers,site_id):
    '''
    Script for finding all connected switches at a site
    '''
    api_url = '{}sites/{}/stats/devices?type=switch'.format(mist_url,site_id)
    #print(api_url)
    online_devices = ''
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        devices = json.loads(response.content.decode('utf-8'))
        online_devices = []
        for device in devices:
            if device['status'] == 'connected':
                online_devices.append({'device-id': device['id'],'network': device['ip']})
                #print(device['id'] + ':' + device['ip'])
    return online_devices

def find_new_site_from_ip(site_list,ip_address):
    '''
    Find site id from site list based on ip address.
    '''
    site_id = ''
    for site in site_list:
        if IPAddress(ip_address) in IPNetwork(str(site['network'])):
            #print('Ip address {} is a part of network {} at site {}'.format(ip_address,site['network'],site['site-id']))
            site_id = site['site-id']
    return site_id

def move_device_to_new_site(mist_url,headers,old_site_id,device_id,new_site_id):
    '''
    Script to move connected switch from a site to another
    '''
    [tmp,device_stat_info] = get_switch_stat_info(mist_url,headers,old_site_id,device_id)
    org_id =  get_device_stat_info(device_stat_info,'org_id')
    mac_address = get_device_stat_info(device_stat_info,'mac')
    api_url = '{}orgs/{}/inventory'.format(mist_url,org_id)
    reassign_info = { "op": "assign",
        "site_id": new_site_id,
        "macs": [mac_address],
        "no_reassign": False,
        "disable_auto_config": False,
        "managed": True
        }
    response = requests.put(api_url, json=reassign_info, headers=headers)
    if response.status_code != 200:
        print('Failure moving device-id {} from staging site {} to new site {}.'.format(device_id,old_site_id,new_site_id))
    else:
        output = json.loads(response.content.decode('utf-8'))
        print('Device-id {} with mac {} successfully moved from staging site {} to new site {}'.format(device_id,output['success'][0],old_site_id,new_site_id ))

def main():
    '''
    Main function
    '''
    token = read_tokenfile('token')
    site_list = read_csv_file('autoprovision_site_list.csv')
    mist_url = 'https://api.mist.com/api/v1/'
    headers = {'Content-Type': 'application/json',
             'Authorization': 'Token {}'.format(token)}
    staging_devices = check_site_for_connected_switches(mist_url,headers,staging_site_id)
    for device in staging_devices:
        new_site_id = find_new_site_from_ip(site_list,device['network'])
        move_device_to_new_site(mist_url,headers,staging_site_id,device['device-id'],new_site_id)

if __name__ == '__main__':
    #Reading attributes
    if len(sys.argv) == 2+1:
        csv_file = sys.argv[1]
        if validate_mist_id(sys.argv[2]):
                staging_site_id = sys.argv[2]
        else:
            staging_site_id =''
        main()
    else:
        print("Wrong number of arguments")
