#!/usr/bin/env python3
#
# Author: Hans Kristian Eiken, hans@eikjen.no
#
# Script to reboot one switch typically after upgrade by Mist API
#
# Dependent of a token saved in a file named "tokenfile",
# containing only the token on a single line.
#
# Usage: ./reboot_switch site_id device_id
#
# This is not a production ready script, but a proof of
# capabilities quickly thrown together.
#

import json
import requests
import sys

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

#Function to reboot device (typically after upgrade)
def reboot_switch(mist_url,headers,site_id,device_id):
    api_url = '{0}sites/{1}/devices/{2}/restart'.format(mist_url,site_id,device_id)
    #print (api_url)
    post_message = "{ \"device_ids\": [\"" + device_id + "\"]}"
    #print (post_message)
    response = requests.post(api_url, data=post_message, headers=headers)
    reply = json.loads(response.content.decode('utf-8'))
    device_name = get_switch_name(mist_url,headers,site_id,device_id)
    #print(reply)
    if response.status_code == 200:
        return_text =  "\nDevice name       : {}\n".format(device_name)
        return_text +=   "Reboot status      : Success requesting reboot to the API.\n"
    else:
        return_text = "\nDevice name       : {}\n".format(device_name)
        return_text +=  "Reboot status     :  Reboot failed\n" + "\n"
        return_text +=  "Detail: {}\n\n".format(reply['detail'])
    print(return_text)

#Main function
def main():
     token = read_tokenfile("token")
     mist_url = 'https://api.mist.com/api/v1/'
     headers = {'Content-Type': 'application/json',
             'Authorization': 'Token {}'.format(token)}
     reboot_switch(mist_url,headers,site_id,device_id)

if __name__ == '__main__':
    #Reading attributes
    if len(sys.argv) == 2+1:
        site_id = sys.argv[1]
        device_id = sys.argv[2]
        main()
    else:
        print("Wrong number of arguments")
