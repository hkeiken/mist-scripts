#!/usr/bin/env python3
#
# Author: Hans Kristian Eiken, hans@eikjen.no
#
# Script to autoprovision Juniper EX switches when they
# show up at a staging site to a new site based on list attached.
#
# Dependent of a token saved in a file named "token",
# containing only the token on a single line.
#
# Usage for site info: ./ex_autoprovision.py site_list.csv staging_site_id
#
# This is not a production ready script, but a proof of
# capabilities quickly thrown together.
#

import json
import requests
import sys
import csv
from netaddr import IPNetwork, IPAddress

# Function to read "tokenfile", a file containing only a token for Mist API
def read_tokenfile(tokenfile):
    file = open(tokenfile, "r")
    token = file.readline().strip()
    file.close()
    return(token)

#Function to read csv file of sites.
# Should be a first info line and the rest of lines should
# contain network;site-id;more
# network - network for management network id
# site-id - Mist id for site
#   more can be one or more field for humans, typically site name
#   or other information. The script only uses the two first
#   columns.
def read_csv_file(csv_file_name):
    with open(csv_file_name, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file,delimiter=';')
        line_count = 0
        site_list = []
        for row in csv_reader:
            site_list.append({'network': row['Network'],'site-id' :row['Site-id']})
    return site_list #Returned site_list dictionary

def get_device_stat_info(device_stat_info,type):
    if isinstance(device_stat_info[type],str):
        return_text = device_stat_info[type]
    else:
        return_text = "Error, no info"
    return return_text

# Function to get stat info per switch
def get_switch_stat_info(mist_url,headers,site_id,device_id):
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

# Find site id from site list based on ip address.
def find_new_site_from_ip(site_list,ip_address):
    site_id = ''
    for site in site_list:
        if IPAddress(ip_address) in IPNetwork(str(site['network'])):
            #print('Ip address {} is a part of network {} at site {}'.format(ip_address,site['network'],site['site-id']))
            site_id = site['site-id']
    return site_id

def move_device_to_new_site(mist_url,headers,old_site_id,device_id,new_site_id):
    [tmp,device_stat_info] = get_switch_stat_info(mist_url,headers,old_site_id,device_id)
    org_id =  get_device_stat_info(device_stat_info,'org_id')
    mac_address = get_device_stat_info(device_stat_info,'mac')
    api_url = '{}orgs/{}/inventory'.format(mist_url,org_id)
    #print(api_url)

    reassign_info = { "op": "assign",
        "site_id": new_site_id,
        "macs": [mac_address],
        "no_reassign": False,
        "disable_auto_config": False,
        "managed": True
        }

    response = requests.put(api_url, json=reassign_info, headers=headers)
    if response.status_code != 200:
        print('Failure moving device {} from staging site {} to new site {}.'.format(device_id,old_site_id,new_site_id))
    else:
        output = json.loads(response.content.decode('utf-8'))
        #print(output)
        print('Device {} successfully moved from staging site {} to new site {}'.format(device_id,old_site_id,new_site_id ))
        print('API reply success for mac {}.\n'.format(output['success'][0]))

#Main function
def main():
     token = read_tokenfile('token')
     site_list = read_csv_file('autoprovision_site_list.csv')
     mist_url = 'https://api.mist.com/api/v1/'
     headers = {'Content-Type': 'application/json',
             'Authorization': 'Token {}'.format(token)}
     staging_devices = check_site_for_connected_switches(mist_url,headers,staging_site_id)
     for device in staging_devices:
         new_site_id = find_new_site_from_ip(site_list,device['network'])
         #print('Device ' + device['device-id'] + ' with ip ' + device['network'] + ' will be moved from site ' + staging_site_id + ' to new site '+ new_site_id)
         move_device_to_new_site(mist_url,headers,staging_site_id,device['device-id'],new_site_id)
         #print('site-id:' + device['site-id'] + ' ip:' + device['ip'])
     #upgrade_switch(mist_url,headers,site_id,device_id,version_name)

if __name__ == '__main__':
    #Reading attributes
    if len(sys.argv) == 2+1:
        csv_file = sys.argv[1]
        staging_site_id = sys.argv[2]
        main()
    else:
        print("Wrong number of arguments")
