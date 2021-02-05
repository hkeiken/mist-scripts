## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [How to use](#use)
## General info
This is a small project to use Mist API (www.mist.com) API on
switches to replicate the access point feature of autoprovisioning
the devices. The work-around works this way:

- The devices are assigned to a "Staging" site in the organization.
- The script is run regulary, perhaps every 5 minutes or hour.
- The script check thru the staging site and looks for online
  devices.
- If an online device is found, the device is reassigned from
  staging site to a new site based on management address of the
  device in the csv-file.

This is a quick set of scripts to prove functions, not considered
a production ready script.

## Technologies
The project uses Python 3 with a few standard libraries.

## Setup
To run this project, copy the files and create a file named "token" in the same directory containing your Mist API token. To generate token, see the first 25 seconds of the video at this page and follow the instructions: https://www.mist.com/documentation/using-postman/

All the scripts should also have execute rights (chmod 700 scriptname.py)

## How to use

### One-time use:

Input is csv file where an example is in the reprosity and the staging site id.

Example of use: 

```
% ./ex_autoprovision.py autoprovision_site_list.csv abc9e251-65c5-40a2-9757-7ad39cc8e344
Device-id 00000000-0000-0000-1000-f4bfa806babc with mac f4bfa806babc successfully moved from staging site abc9e251-65c5-40a2-9757-7ad39cc8e344 to new site abcf02e3-8c11-4aef-b3f7-7a5284471c4f
```

### Regular use:

Run this script from a cron file to run it regulary.
