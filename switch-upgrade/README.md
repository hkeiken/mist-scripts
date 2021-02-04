## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)
* [How to use](#use)
## General info
This is a small project to use Mist API (www.mist.com) feature of
upgrading Juniper EX switches with API. When this code was written, the feature existed in the API, but not in the GUI. This is supposed to become a GUI feature at some point.

This is a quick set of scripts to prove functions. There are lack of input and message validations so this is not production ready.

## Technologies
The project uses Python 3 with a few standard libraries.

## Setup
To run this project, copy the files and create a file named "token" in the same directory containing your Mist API token. To generate token, see the first 25 seconds of the video at this page and follow the instructions: https://www.mist.com/documentation/using-postman/

All the scripts should also have execute rights (chmod 700 scriptname.py)

## How to use

### Info gathering: fetch_switch_info.py

This switch is to gather information about switches. It uses either just a site-id to show information of all switches at a site or both site-id and switch-id to gather information about a specific switch.

Example for site only:

```
% ./fetch_switch_info.py abc74fc3-8819-4cf0-b318-b7be37b21b7d
--------------
Site name         : Test site
Site id           : abc74fc3-8819-4cf0-b318-b7be37b21b7d
--------------
Device name         : ex2300-test
Device id           : 00000000-0000-0000-1000-f4bfa806babc
Device management ip: 10.10.10.239
Device Model        : EX2300-C-12P
Device status       : connected
Current version     : 19.3R1.8
Potential versions  : 18.4R2.7 19.3R1.8
Mist config status  : Configured by Mist
Upgrade progress    : 10
Upgrade status      : upgrading
Upgrade status id   : 3035
--------------
```
Example for switch only information. Typically used during upgrade or during reboot to gather switch specific information.
```
% ./fetch_switch_info.py abc74fc3-8819-4cf0-b318-b7be37b21b7d 00000000-0000-0000-1000-f4bfa806babc

Device name         : ex2300-test
Device id           : 00000000-0000-0000-1000-f4bfa806babc
Device management ip: 10.10.10.239
Device Model        : EX2300-C-12P
Device status       : connected
Current version     : 19.3R1.8
Potential versions  : 18.4R2.7 19.3R1.8
Mist config status  : Configured by Mist
Upgrade progress    : 100
Upgrade status      : upgrading
Upgrade status id   : 3037
```

Comments around information:

- Potential versions are the versions Mist API supports upgrading to. These versions can be upgraded/downgraded without manual copying software to the switch. If one want other versions than these, the API do not support the process.
- Upgrade status id is unknown what it means.

### Upgrade script: upgrade_switch.py

This script initiates upgrade of a switch. The script takes site-id, switch-id and version as input. The only allowed versions are the ones listed as "Potential versions" in the info gathering script output.

Example:

```
% ./upgrade_switch.py abc74fc3-8819-4cf0-b318-b7be37b21b7d 00000000-0000-0000-1000-f4bfa806babc 19.3R1.8

Device name       : ex2300-test
Upgrade status    : starting
```

The Mist API do not give a lot of feedback during upgrades. The best way to manage an upgrade is to observe the info gathering script "Device status" change from upgrading to connected. When this is changed, the upgrade is finished but the switch still needs rebooting. After the reboot the "Upgrade status" changes to success.

### Reboot script: reboot_switch.py

This script initiates reboot of the switch. Typically a reboot of a Juniper EX switch takes 10-15 minutes.

Example:

```
% ./reboot_switch.py abc74fc3-8819-4cf0-b318-b7be37b21b7d 00000000-0000-0000-1000-f4bfa806babc

Device name       : ex2300-test
Reboot status     : Success requesting reboot to the API.
```
