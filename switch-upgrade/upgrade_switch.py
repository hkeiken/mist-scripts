#!/usr/bin/env python3
#
# Author: Hans Kristian Eiken, hans@eikjen.no
#
# Script to upgrade one switch to a new software version from Mist API
#
# Dependent of a token saved in a file named "tokenfile",
# containing only the token on a single line.
#
# Usage: ./upgrade_switch site_id device_id version
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

#Function to get switch name from device_id
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

#Function to upgrade switch
def upgrade_switch(mist_url,headers,site_id,device_id,version_name):
    token = read_tokenfile("token")
    mist_url = 'https://api.mist.com/api/v1/'
    headers = {'Content-Type': 'application/json',
                 'Authorization': 'Token {}'.format(token)}

    api_url = '{0}sites/{1}/devices/{2}/upgrade'.format(mist_url,site_id,device_id)
    post_message = "{ \"version\": \"" + version_name + "\" }"
    response = requests.post(api_url, data=post_message, headers=headers)
    reply = json.loads(response.content.decode('utf-8'))
    device_name = get_switch_name(mist_url,headers,site_id,device_id)
    #print(reply)
    if response.status_code == 200:
        return_text = "\n"
        return_text +=  "Device name       : {}".format(device_name) + "\n"
        return_text += "Upgrade status    : {}".format(reply['status']) + "\n"
    else:
        return_text =  "upgrade failed"
    print(return_text)

#Main function
def main():
     token = read_tokenfile("token")
     mist_url = 'https://api.mist.com/api/v1/'
     headers = {'Content-Type': 'application/json',
             'Authorization': 'Token {}'.format(token)}
     upgrade_switch(mist_url,headers,site_id,device_id,version_name)

if __name__ == '__main__':
    #Reading attributes
    if len(sys.argv) == 3+1:
        site_id = sys.argv[1]
        device_id = sys.argv[2]
        version_name = sys.argv[3]
        main()
    else:
        print("Wrong number of arguments")
