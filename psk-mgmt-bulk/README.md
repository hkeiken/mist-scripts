## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [How to use](#use)
## General info
This is a small project to use Mist API (www.mist.com) feature of
single SSID with multiple pre-shared keys. The script bulk add and delete keys.

This is not a production ready script, but a proof of capabilities quickly thrown together.

## Technologies
The project uses Python 3 with a few standard libraries.

## Setup
To run this project, copy the files and create a file named "token" in the same directory containing your Mist API token. To generate token, see the first 25 seconds of the video at this page and follow the instructions: https://www.mist.com/documentation/using-postman/

All the scripts should also have execute rights (chmod 700 psk-mgmt-bulk.py)

## How to use
```
Example csv_file:
id;key;ssid;password;vlan
1;room101;skurva-hotell;1234;30
2;room102;skurva-hotell;1000;31

```
Example use:

Adds key:
```
% ./psk-mgmt-bulk.py add 18bf02e3-0000-0000-0000-00000000000 psk-mgmt-bulk.csv
PSK room101 created at site "Test" successfully
PSK room102 created at site "Test" successfully
```

Delete uses the same csv_file, but only the key field is used for deletion:
```
% ./psk-mgmt-bulk.py delete 18bf02e3-0000-0000-0000-000000000000 psk-mgmt-bulk.csv
Sucessfully deleted PSK room101 at site "Test"
Sucessfully deleted PSK room102 at site "Test"
```
