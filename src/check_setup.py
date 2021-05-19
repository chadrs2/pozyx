#!/usr/bin/python3

#from pypozyx import PozyxSerial, get_first_pozyx_serial_port, POZYX_SUCCESS, SingleRegister, EulerAngles, Acceleration
from pypozyx import *
from pypozyx.definitions.registers import POZYX_FIRMWARE_VER, POZYX_WHO_AM_I
from pypozyx.lib import Device


if __name__ == "__main__":
    # Master Tag serial port
    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()
    
    # Device ID Config
    remote_id = 0x7607                 # remote tag device network ID
    
    pozyx = PozyxSerial(serial_port)

    data = SingleRegister()
    pozyx.getRead(POZYX_WHO_AM_I, data, remote_id=remote_id)
    print('who am i: 0x%0.2x' % data[0])
    
    data = SingleRegister()
    pozyx.getRead(POZYX_FIRMWARE_VER, data, remote_id=remote_id)
    print('firmware version: 0x%0.2x' % data[0])

    data = SingleRegister()
    pozyx.getRead(POZYX_FIRMWARE_VER, data, remote_id=remote_id)
    print('hardware version: 0x%0.2x' % data[0])

    data = SingleRegister()
    pozyx.getRead(POZYX_FIRMWARE_VER, data, remote_id=remote_id)
    print('self test result: %s' % bin(data[0]))

    data = SingleRegister()
    pozyx.getRead(POZYX_FIRMWARE_VER, data, remote_id=remote_id)
    print('error: 0x%0.2x' % data[0])

    