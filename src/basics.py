#!/usr/bin/python3

#from pypozyx import PozyxSerial, get_first_pozyx_serial_port, POZYX_SUCCESS, SingleRegister, EulerAngles, Acceleration
from pypozyx import *

## Initialize Pozyx
serial_port = get_first_pozyx_serial_port()

if serial_port is not None:
    print(serial_port)
    pozyx = PozyxSerial(serial_port)
    print("Connection successful!")
else:
    print("No pozyx port found")

## Reading Data
# initialize data container
who_am_i = SingleRegister()
# get the data, passing along the container
status = pozyx.getWhoAmI(who_am_i)

# check the status to see if the read was successful. Handling failure is covered later.
if status == POZYX_SUCCESS:
    # print the container. Note how a SingleRegister will print as a hex string by default.
    print(who_am_i) # will print '0x43'

# and repeat
# initialize the data container
acceleration = Acceleration()
# get the data, passing along the container
pozyx.getAcceleration_mg(acceleration)

# initialize the data container
t = 0
while t < 50:
    euler_angles = EulerAngles()
    # get the data, passing along the container
    pozyx.getEulerAngles_deg(euler_angles)
    print("Euler Angles:",euler_angles)
    
    t += 1

## Writing Data
'''
# method 1: making a data object
# this is much more readable
uwb_settings = UWBSettings(channel=5, bitrate=1, prf=2, plen=0x08, gain_db=25.0)
pozyx.setUWBChannel(uwb_channel)
# method 2: using the register values directly
# this isn't readable and also not writable (need to search in depth register documentation)
pozyx.setUWBSettings([5, 0b10000001, 0x08, 50])

pozyx.setPositionAlgorithm(PozyxConstants.POSITIONING_ALGORITHM_UWB_ONLY)
new_id = NetworkId(0x1)
pozyx.setNetworkId(new_id)
pozyx.setPositioningFilter(PozyxConstant.FILTER_TYPE_MOVING_AVERAGE, 10)

# assume an anchor 0x6038 that we want to add to the device list and immediately save the device list after.
anchor = DeviceCoordinates(0x6038, 0, Coordinates(5000, 5000, 0))
pozyx.addDevice(anchor)
pozyx.saveNetwork()
# after, we can start positioning. Positioning takes its parameters from the configuration in the tag's
# registers, and so we only need the coordinates.
position = Coordinates()
pozyx.doPositioning(position)
'''

## Saving Writable Register Data
'''
# Saves the positioning settings
pozyx.savePositioningSettings()
# Saves the device list used for positioning
pozyx.saveNetwork()
# Saves the device's UWB settings
pozyx.saveUWBSettings()
'''

