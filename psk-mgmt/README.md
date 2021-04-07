## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [How to use](#use)
## General info
This is a small project to use Mist API (www.mist.com) feature of
single SSID with multiple pre-shared keys to handle vlans per key.
Since currently the pre-shared key vlan-ids are not supported in
the Mist Web-UI, this have to be done using the API. The feature
will probably come to the Web-UI at some point.

This is not a production ready script, but a proof of capabilities quickly thrown together.

## Technologies
The project uses Python 3 with a few standard libraries.

## Setup
To run this project, copy the files and create a file named "token" in the same directory containing your Mist API token. To generate token, see the first 25 seconds of the video at this page and follow the instructions: https://www.mist.com/documentation/using-postman/

All the scripts should also have execute rights (chmod 700 psk-mgmt.py)

## How to use

Example for adding pre-shared key:

```
./psk-mgmt.py add 18bf02e3-0000-0000-0000-7a5284471c4f rom100 skurva-hotell 123 1234
PSK rom100 created at site "Osloveien 1" successfully
```

Example for deleting pre-shared key:

```
./psk-mgmt.py delete 18bf02e3-0000-0000-0000-7a5284471c4f test1
Sucessfully deleted PSK test1 at site "Osloveien 1"
```

Example for showing pre-shared key:

```
./psk-mgmt.py show 18bf02e3-0000-0000-0000-7a5284471c4f rom100
Site name: Osloveien 1
Site id:   18bf02e3-0000-0000-0000-7a5284471c4f
Key name:  rom100
SSID:      skurva-hotell
Vlan id:   123
Password:  1234
```
Example for updating existing key:

```
./psk-mgmt.py update 18bf02e3-0000-0000-0000-7a5284471c4f rom100 test2
Updated key rom100 with new password
```
