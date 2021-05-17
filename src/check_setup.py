#!/usr/bin/python3

#from pypozyx import PozyxSerial, get_first_pozyx_serial_port, POZYX_SUCCESS, SingleRegister, EulerAngles, Acceleration
from pypozyx import *

from pypozyx.lib import Device


if __name__ == "__main__":
    # Master Tag serial port
    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()
    
    # Device ID Config
    remote_id = 0x7607                 # remote tag device network ID
    anchor1_id = 0x7612                  # anchor device network ID
    
    pozyx = PozyxSerial(serial_port)

    # Change UWB settings:
    ''' HOW TO CHANGE UWB SETTINGS:
    ## Set the Pozyx's UWB settings.
    # If using this remotely, remember to change the local UWB settings as well
    # to make sure you are still able to communicate with the remote device.
    # Max Range :=: channel := 2(optimal); bitrate := 0(lower); plen := 0x0c(i.e. 4096 symbols)(higher)
    # Max Rate :=: channel := 5(high); bitrate := 2(higher); plen := 0x08(i.e. 1024 symbols)(lower)  
    uwb_settings = UWBSettings(channel=5, bitrate=1, prf=2, plen=0x08, gain_db=25.0)
    pozyx.setUWBSettings(self, uwb_settings, remote_id=None, save_to_flash=False)

    BITRATES = {0: '110 kbit/s', 1: '850 kbit/s', 2: '6.81 Mbit/s'}
    PRFS = {1: '16 MHz', 2: '64 MHz'}
    PREAMBLE_LENGTHS = {0x0C: '4096 symbols', 0x28: '2048 symbols', 0x18: '1536 symbols', 0x08: '1024 symbols',
                 0x34: '512 symbols', 0x24: '256 symbols', 0x14: '128 symbols', 0x04: '64 symbols'}

    # assume an anchor 0x6038 that we want to add to the device list and immediately save the device list after.
    anchor = DeviceCoordinates(0x6038, 0, Coordinates(5000, 5000, 0))
    pozyx.addDevice(anchor)
    pozyx.saveNetwork()

    ## Saving Writable Register Data
    # Saves the device list used for positioning
    pozyx.saveNetwork()
    # Saves the device's UWB settings
    pozyx.saveUWBSettings()
    '''
    pozyx.clearDevices(remote_id)
    pozyx.clearDevices()
    # pozyx.addDevice(DeviceCoordinates(remote_id,0,Coordinates(0,0,0)))

    # WORKING SETTINGS: UWBSettings(channel=5,bitrate=0,prf=2,plen=0x08,gain_db=11.5)
    # uwb_settings = UWBSettings(channel=5,bitrate=0,prf=2,plen=0x08,gain_db=11.5)
    # # uwb_settings = UWBSettings(channel=2,bitrate=0,prf=2,plen=0x08,gain_db=15.5)
    # status = pozyx.setUWBSettings(uwb_settings=uwb_settings,remote_id=remote_id)
    # status = pozyx.setUWBSettings(uwb_settings=uwb_settings)

    pozyx.addDevice(DeviceCoordinates(remote_id,1,Coordinates(0,0,0)))

    anchor = DeviceCoordinates(anchor1_id, 0, Coordinates(0,0,0))
    pozyx.addDevice(anchor,remote_id=remote_id)
    anchor = DeviceCoordinates(anchor1_id, 0, Coordinates(0,0,0))
    pozyx.addDevice(anchor)

    # status &= pozyx.setUWBChannel(2,remote_id=remote_id)
    # status &= pozyx.setUWBChannel(2)
    # status = pozyx.clearConfiguration()
    # status &= pozyx.clearConfiguration(remote_id)
    
    # Get and Print UWB Settings
    curr_master_uwb_settings = UWBSettings()
    curr_tag_uwb_settings = UWBSettings()
    status = pozyx.getUWBSettings(curr_master_uwb_settings)
    status = pozyx.getUWBSettings(curr_tag_uwb_settings,remote_id)
    curr_anch_uwb_settings = UWBSettings()

    list_size = SingleRegister()
    pozyx.getDeviceListSize(list_size)
    dl_master = DeviceList(list_size=list_size[0])
    status = pozyx.getDeviceIds(dl_master)
    pozyx.getDeviceListSize(list_size,remote_id=remote_id)
    dl_slave = DeviceList(list_size=list_size[0])
    status = pozyx.getDeviceIds(dl_slave,remote_id=remote_id)
    
    if status == POZYX_SUCCESS:
        print('Master UWB Settings => Channel: {}, Bitrate: {}, PRF: {}, Plen: {}, Gain(dB): {}'.\
            format(curr_master_uwb_settings.channel,UWBMapping.BITRATES[curr_master_uwb_settings.bitrate],\
                UWBMapping.PRFS[curr_master_uwb_settings.prf],UWBMapping.PREAMBLE_LENGTHS[curr_master_uwb_settings.plen],\
                curr_master_uwb_settings.gain_db))
        print('Slave UWB Settings => Channel: {}, Bitrate: {}, PRF: {}, Plen: {}, Gain(dB): {}'.\
            format(curr_tag_uwb_settings.channel,UWBMapping.BITRATES[curr_tag_uwb_settings.bitrate],\
                UWBMapping.PRFS[curr_tag_uwb_settings.prf],UWBMapping.PREAMBLE_LENGTHS[curr_tag_uwb_settings.plen],\
                curr_tag_uwb_settings.gain_db))
        # print("Master:",dl_master)
        print("Master Device IDs:")
        for id in dl_master.data[:]:
            print("Decimal:",id,"Hexidecimal:",hex(id))
        # print("Slave Device:",dl_slave)
        print("Slave Device IDs:")
        for id in dl_slave.data[:]:
            print("Decimal:",id,"Hexidecimal:",hex(id))
    else:
        print("UWB Setting Retrieval Failed!")
        quit()