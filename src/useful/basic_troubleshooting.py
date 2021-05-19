#!/usr/bin/env python
"""
Pozyx basic troubleshooting (c) Pozyx Labs 2017

If you're experiencing trouble with Pozyx, this should be your first step to check for problems.
Please read the article on https://www.pozyx.io/Documentation/Tutorials/troubleshoot_basics/Python
"""

from pypozyx import PozyxSerial, get_first_pozyx_serial_port, PozyxConstants, POZYX_SUCCESS
from pypozyx.structures.device_information import DeviceDetails
from pypozyx.definitions.registers import POZYX_WHO_AM_I


def device_check(pozyx, remote_id=None):
    system_details = DeviceDetails()
    pozyx.getDeviceDetails(system_details, remote_id=remote_id)

    if remote_id is None:
        print("Local %s with id 0x%0.4x" % (system_details.device_name, system_details.id))
    else:
        print("%s with id 0x%0.4x" % (system_details.device_name.capitalize(), system_details.id))

    print("\tWho am i: 0x%0.2x" % system_details.who_am_i)
    print("\tFirmware version: v%s" % system_details.firmware_version_string)
    print("\tHardware version: v%s" % system_details.hardware_version_string)
    print("\tSelftest result: %s" % system_details.selftest_string)
    print("\tError: 0x%0.2x" % system_details.error_code)
    print("\tError message: %s" % system_details.error_message)


def network_check_discovery(pozyx, remote_id=None):
    pozyx.clearDevices(remote_id)
    if pozyx.doDiscovery(discovery_type=PozyxConstants.DISCOVERY_ALL_DEVICES, remote_id=remote_id) == POZYX_SUCCESS:
        print("Found devices:")
        pozyx.printDeviceList(remote_id, include_coordinates=False)


if __name__ == '__main__':
    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()

    pozyx = PozyxSerial(serial_port)

    # change to remote ID for troubleshooting that device
    remote_id = 0x7612#None#0x7607

    '''
    EX:
    who am i: 0x43
    firmware version: 0x10
    hardware version: 0x23
    self test result: 0b111111
    error: 0

    who am i is wrong: 
        the Pozyx device is not running or it is badly connected with the Arduino. 
        Make sure that the jumper is on the BOOT0 pins.
    firmware version is wrong: 
        you must update the firmware as explained in updating the firmware. 
        Make sure that all devices, anchors and tags are running on the same firmware version.
    Hardware version is wrong: 
        is your device on fire?
    Self test is different: 
        for the tag the result should be 0b111111, for the anchor it should be 0b110000. 
        Check out POZYX_ST_RESULT for more information. 
        Note: in firmware version 1.0, the self-test might currently display 0b110000 instead of 0b111111. 
        This is an anomaly which occurs when the selftest is done before the sensors are initialized. 
        Don't panic, this doesn't necessarily mean the sensors aren't initialized. 
        You can try the third tutorial to quickly see whether the IMU is actually operational.
        Check if the problem remains after resetting the device.
    The error code is not 0: 
        Something went wrong, this isn't necessarily dramatic. 
        Check out POZYX_ERRORCODE to see which error was triggered. 
        If you see error 0x09, you can safely ignore this.
    '''
    device_check(pozyx, remote_id)
    network_check_discovery(pozyx, remote_id)
