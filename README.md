# POZYX UWB SENSORS

## Contents
* [Overview](#set-up-a-base-station-or-personal-computer)
* [Software Installation](#software-installation)
* [Hardware Setup](#hardware-setup)
* [Helpful Code Snippets](#helpful-code-snippets)
* [Full Example Range Test](#full-example-range-test)

## Requirements
* [Ubuntu 18.04](https://ubuntu.com/download/desktop)
* [Git](https://git-scm.com/download/linux)

## Important Links
* [How UWB Works](https://pozyx.io/uwb-technology/how-does-uwb-work/)
* [POZYX Main Website](https://pozyx.io/)
* [pypozyx Docs](https://pypozyx.readthedocs.io/en/develop/)
* [POZYX Python Guide](https://docs.pozyx.io/creator/latest/python)

------------

## Overview

The purpose of UWB sensors in the GPS denied convoy problem is to provide accurate range measurements between immediate neighboring vehicles. 
These range measurements provide information for longitudinal and lateral control. 
They can also be utilized for correctly updating our path planning algorithms in convoy scenarios.
Through review of a variety of UWB sensors, [POZYX's](see https://pozyx.io/) UWB sensors have been chosen.

This readme has been made to help any first time user understand what pozyx is, how we are using the sensors for our convoy application, and how to personally start getting range measurements from a few sensors.

**Note** This is based on the Creator Kit provided by ASI.

### POZYX UWB SENSORS
The pozyx sensors were originally designed for a setup consisting of placing 4 or more sensors around an area thus outlining a workspace. 
These sensors are known as Anchors. Sensors within this outline are then used for accurate 2D-3D positioning and tracking. 
These sensors are called Tags. This works by having the Tags send UWB-pulses to each of the surrounding Anchors to get time-of-flight range measurements. 
These range measurements are then triangulated to get a position of each Tag within the workspace. 
Additionally, one can control multiple tags wirelessly with one master tag connected to a computer.

We have utilized pozyx’s powerful UWB sensors in a different setup for the convoy problem. 
Since Tags can already get ranges from Anchors, that ability can then be utilized in our convoy problem to get range measurements between vehicles without the need for setting up anchors around a predetermined workspace. 

------------

## Sofware Installation
1. Install pypozyx:
```pip3 install pypozyx``` or ```python3 -m pip install pypozyx```

2. Install pozyx's [Companion Software](https://pozyx.io/products-and-services/creator-controller)

------------

## Hardware Setup
1. Charge all batteries that come with the kit
2. Plug one tag into your computer, another into a battery, and grab an anchor and plug it into another battery
3. If you want, the anchor works better on a vertical surface. You can add a velcro strip to any small portable box so that the anchor can stay verticle even if you need to move it. 

That's it! The next two sections are meant to help you get started into the code and running tests.

------------

## Helpful Code Snippets
The following are various important lines of code and what they do:

1. Connecting your code to the pozyx software in python:
```
serial_port = get_first_pozyx_serial_port()
if serial_port is None:
    print("No Pozyx connected. Check your USB cable or your driver!")
    quit()
pozyx = PozyxSerial(serial_port)
```
2. Find what pozyx devices are connected to the Master tag and what their respective id's are:
```
if pozyx.doDiscovery(discovery_type=PozyxConstants.DISCOVERY_ALL_DEVICES) == POZYX_SUCCESS:
        print("Found devices:")
        pozyx.printDeviceList(None, include_coordinates=False)
```
3. Add anchors or tags to the Master Tag:
```
pozyx.clearDevices()
# For adding tags
tag_id = 0x007 # some hex number relating to the added device found in part 2
pozyx.addDevice(DeviceCoordinates(tag_id,1,Coordinates(0,0,0)))
# For adding anchors
anchor_id = 0x008
pozyx.addDevice(DeviceCoordinates(anchor_id,0,Coordinates(0,0,0)))
```
5. Add anchors to a slave tag:
```
slave_tag_id = 0x007
pozyx.clearDevices(remote_id=slave_tag_id)
# For adding anchors
anchor_id = 0x008
pozyx.addDevice(DeviceCoordinates(anchor_id,0,Coordinates(0,0,0)),remote_id=slave_tag_id)
```
6. Get the range measurement between two sensors:
```
device_range = DeviceRange()
# Getting range between an Anchor and Tag
status = self.pozyx.doRanging(anchor_id, device_range, tag_id)
if status == POZYX_SUCCESS:
  print("Range =",device_range.distance,"detected at",device_range.timestamp,"ms")
# Getting range between Master and Slave Tags
status = self.pozyx.doRanging(slave_tag_id, device_range, None)
if status == POZYX_SUCCESS:
  print("Range =",device_range.distance,"detected at",device_range.timestamp,"ms")
```
7. Get other sensor information:
```
# Set remote_id to a tags id if you want sensor information from that tag
orientation = EulerAngles()
acceleration = Acceleration()
pozyx.getEulerAngles_deg(orientation, remote_id=None)
pozyx.getAcceleration_mg(acceleration, remote_id=None)
print("Orientation: %s, acceleration: %s" % (str(orientation), str(acceleration))
```
Continue the same process above to get temperature, magnetometer, pressure, other sensor information. See the [pypozyx docs](https://pypozyx.readthedocs.io/en/develop/pypozyx_api/index.html) for the available getter functions.

8. Catching errors example for doRanging() function:
```
 if status != PZYX_SUCCESS:
    error_code = SingleRegister()
    status = self.pozyx.getErrorCode(error_code)
    if status == POZYX_SUCCESS:
        print("ERROR Ranging, local %s" %
        self.pozyx.getErrorMessage(error_code))
    else:
        print("ERROR Ranging, couldn't retrieve local error")
```
9. Other helpful code files relating to changing and updating UWB settings (this is really important to get better max ranges!!):
They can all be found in [this](https://github.com/pozyxLabs/Pozyx-Python-library/tree/master/useful) github folder from pypozyx.


------------

## Full Example Range Test

------------
