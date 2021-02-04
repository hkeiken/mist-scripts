#!/usr/bin/env python3
#
# Author: Hans Kristian Eiken, hans@eikjen.no
#
# Script to fetch status for switches at a site or specific switch
#
# Dependent of a token saved in a file named "tokenfile",
# containing only the token on a single line.
#
# Usage for site info: ./upgrade_switch site_id
# Usage for swithc info: ./upgrade_switch site_id device_id
#
# This is not a production ready script, but a proof of
# capabilities quickly thrown together.
#

import json
import requests
import sys
from pprint import pprint
from collections import defaultdict

# Function to read "tokenfile", a file containing only a token for Mist API
def read_tokenfile(tokenfile):
    file = open(tokenfile, "r")
    token = file.readline().strip()
    file.close()
    return(token)

#Function to get organization based on device id
def get_device_organization(mist_url,headers,site_id,device_id):
    api_url = '{}sites/{}/devices?type=switch'.format(mist_url,site_id)
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        devices = json.loads(response.content.decode('utf-8'))
        org_id =''
        for device in devices:
            if device['id'] == device_id:
                org_id = device['org_id']
    return org_id


#Function to get last device_id at site (reused to get org)
def get_last_device_at_site(mist_url,headers,site_id):
    api_url = '{}sites/{}/devices?type=switch'.format(mist_url,site_id)
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        devices = json.loads(response.content.decode('utf-8'))
        device_id =''
        for device in devices:
            device_id = device['id']
    return device_id

# Function to read site name from site_id
def get_site_name(mist_url,headers,site_id):
    last_device_id =  get_last_device_at_site(mist_url,headers,site_id)
    org_id = get_device_organization(mist_url,headers,site_id,last_device_id)
    api_url = '{}orgs/{}/sites'.format(mist_url,org_id,site_id)
    response = requests.get(api_url, headers=headers)
    this_site=''
    if response.status_code == 200:
        sites = json.loads(response.content.decode('utf-8'))
        #pprint(response.content)
        for site in sites:
            if site['id'] == site_id:
                this_site = site['name']
    return this_site

#Function to get switch name based on switch id
def get_switch_name(mist_url,headers,site_id,device_id):
    api_url = '{}sites/{}/devices?type=switch'.format(mist_url,site_id)
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        devices = json.loads(response.content.decode('utf-8'))
        device_name =''
        for device in devices:
            if device['id'] == device_id:
                device_name = device['name']
    return device_name

#Function to read versions avable for a switch model
def get_versions_available(mist_url,headers,model):
    api_url = '{}sites/{}/devices/versions?type=switch'.format(mist_url,site_id)
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        version_set = json.loads(response.content.decode('utf-8'))
        models = []
        versions_per_set = defaultdict(list)
        for version in version_set:
            models.append(version['model'])
            versions_per_set[version['model']].append(version['version'])
        unique_models = list(dict.fromkeys(models))
        return versions_per_set[model]

#Function to read monitoring status of a switch
def get_switch_monitoring_state(device_info):
    #print (device_info)
    if device_info['disable_auto_config'] == True:
        return_text = "Not configured by Mist"
    elif device_info['disable_auto_config'] == False:
        return_text = "Configured by Mist"
    else:
        return_text = "Error, no info"
    return return_text

#Function to read monitoring status of a switch
def get_switch_management_ip(device_stat_info):
    if isinstance(device_stat_info['ip'],str):
        return_text = device_stat_info['ip']
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

# Function to get info per switch
def get_switch_info(mist_url,headers,site_id,device_id):
    api_url = '{0}sites/{1}/devices?type=switch'.format(mist_url,site_id)
    #print(api_url)
    response = requests.get(api_url, headers=headers)
    return_bol = False
    device_info = ''
    if response.status_code == 200:
        devices = json.loads(response.content.decode('utf-8'))
        for device in devices:
            device_info = device
            return_bol = True
    else:
        print("Error Fetching switch stat")
    return return_bol,device_info

def gather_switch_data(mist_url,headers,site_id,device_id,device_stat_info):
    [device_info_result,device_info] = get_switch_info(mist_url,headers,site_id,device_id)
    updateinfo = device_stat_info['fwupdate']
    module_stat = device_stat_info['module_stat'][0]
    versions_available = ' '.join(get_versions_available(mist_url,headers,device_stat_info['model']))
    return_text =  "Device name         : {}\n".format(get_switch_name(mist_url,headers,site_id,device_id))
    return_text += "Device id           : {}\n".format(device_id)
    return_text += "Device management ip: {}\n".format(get_switch_management_ip(device_stat_info))
    return_text += "Device Model        : {}\n".format(device_stat_info['model'])
    return_text += "Device status       : {}\n".format(device_stat_info['status'])
    return_text += "Current version     : {}\n".format(module_stat['version'])
    return_text += "Potential versions  : {}\n".format(versions_available)
    return_text += "Mist config status  : {}\n".format(get_switch_monitoring_state(device_info))
    return_text += "Upgrade progress    : {}\n".format(updateinfo['progress'])
    return_text += "Upgrade status      : {}\n".format(updateinfo['status'])
    return_text += "Upgrade status id   : {}\n".format(updateinfo['status_id'])
    #return_text += "Pending version     : {}\n".format(module_stat['pending_version'])
    return return_text

#Function to get switches at a site with model, version and versions available
def get_switches_at_site(mist_url,headers,site_id):
    #api_url = '{}sites/{}/devices?type=switch'.format(mist_url,site_id)
    api_url = '{0}sites/{1}/stats/devices?type=switch'.format(mist_url,site_id)
    #print(api_url)
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        devices = json.loads(response.content.decode('utf-8'))
        #pprint(response.content)
        return_text = "--------------\n"
        return_text += "Site name         : {}\n".format(get_site_name(mist_url,headers,site_id))
        return_text += "Site id           : {}\n".format(site_id)
        return_text += "--------------"
        for device in devices:
            return_text += fetch_switch_status(mist_url,headers,site_id,device['id'])
            return_text += "--------------\n"
    return return_text

#Main function to fetch upgrade status
def fetch_switch_status(mist_url,headers,site_id,device_id):
    api_url = '{0}sites/{1}/stats/devices?type=switch'.format(mist_url,site_id)
    #print (api_url)
    response = requests.get(api_url, headers=headers)
    reply = json.loads(response.content.decode('utf-8'))
    device_name = get_switch_name(mist_url,headers,site_id,device_id)
    if response.status_code == 200:
        for device_reply in reply:
            if device_reply['id'] == device_id:
                return_text = "\n"
                return_text += gather_switch_data(mist_url,headers,site_id,device_id,device_reply)
                #return_text += "\n"
    else:
        return_text = "fetching failed"
    return return_text


#Main function
def main_site():
     token = read_tokenfile("token")
     mist_url = 'https://api.mist.com/api/v1/'
     headers = {'Content-Type': 'application/json',
             'Authorization': 'Token {}'.format(token)}
     print(get_switches_at_site(mist_url,headers,site_id))

#Main function
def main_switch():
     token = read_tokenfile("token")
     mist_url = 'https://api.mist.com/api/v1/'
     headers = {'Content-Type': 'application/json',
             'Authorization': 'Token {}'.format(token)}
     print(fetch_switch_status(mist_url,headers,site_id,device_id))

if __name__ == '__main__':
    #Reading attributes if site info
    if len(sys.argv) == 1+1:
        site_id = sys.argv[1]
        main_site()
    #Reading attributes if device info
    elif len(sys.argv) == 2+1:
        site_id = sys.argv[1]
        device_id = sys.argv[2]
        main_switch()
    else:
        print("Error number of attributes!")
