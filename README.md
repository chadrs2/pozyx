# POZYX UWB SENSORS

## Contents
* [Overview](#set-up-a-base-station-or-personal-computer)
* [Software Installation](#software-installation)
* [Hardware Setup](#faq)
* [Example Test Case](#known-bugs)
* [Important Links](#important-links)

## Requirements
* [Ubuntu 18.04](https://ubuntu.com/download/desktop)
* [Git](https://git-scm.com/download/linux)

----------

## Overview

The purpose of UWB sensors in the GPS denied convoy problem is to provide accurate range measurements between immediate neighboring vehicles. 
These range measurements provide information for longitudinal and lateral control. 
They can also be utilized for correctly updating our path planning algorithms in convoy scenarios.
Through review of a variety of UWB sensors, this code base uses UWB sensors provided by [pozyx](see https://pozyx.io/)

### POZYX UWB SENSORS
The pozyx sensors were originally designed for a setup consisting of placing sensors outlining a workspace. 
These sensors are known as Anchors. Sensors within this outline are then used for accurate 2D-3D positioning and tracking. 
These sensors are called Tags. This works by having the Tags send UWB-pulses to each of the surrounding Anchors to get time-of-flight range measurements. 
These range measurements are then triangulated to get a position of the Tags within the workspace. 
Additionally, one can control multiple tags wirelessly with one master tag connected to a computer.

We have utilized pozyx’s powerful UWB sensors in a different setup for the convoy problem. 
Since Tags can already get ranges from Anchors, that ability can then be utilized in our convoy problem to get range measurements between vehicles without the need for setting up anchors around our workspace. 

------------

## Sofware Installation

1. Clone the repository to your Home directory:
```
cd ~
git clone https://github.com/chadrs2/pozyx.git
```
2. Install pypozyx:
```pip3 install pypozyx``` or ```python3 -m pip install pypozyx```

3. Install pozyx's [Companion Software](https://pozyx.io/products-and-services/creator-controller)

## Hardware Setup


------------

## Example Test Case


------------

## Important Links
* [POZYX Main Website](https://pozyx.io/)
* [PYPOZYX Docs](https://pypozyx.readthedocs.io/en/develop/)
* [POZYX Python Guide](https://docs.pozyx.io/creator/latest/python)

------------
