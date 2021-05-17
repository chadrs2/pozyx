#!/usr/bin/python3

#from pypozyx import PozyxSerial, get_first_pozyx_serial_port, POZYX_SUCCESS, SingleRegister, EulerAngles, Acceleration
from pypozyx import *
import matplotlib.pyplot as plt
import numpy as np
import time

from pypozyx.lib import Device

class Tag2AnchorDistance():
    def __init__(self,pozyx,remote_id,anchor_id):        
        self.pozyx = pozyx

        # Clear all anchors connected to remote id tag
        self.pozyx.clearDevices(remote_id=remote_id)
        
        # Add anchor(s) to remote device
        anchor1 = DeviceCoordinates(anchor_id,0,Coordinates(0,0,0))
        self.pozyx.addDevice(anchor1,remote_id)

        # State Variables
        self.remote_id = remote_id
        self.anchor_id = anchor_id
        self.anchor1 = anchor1
        self.device_range = DeviceRange()
        self.prev_time = None
        self.max_rate = None
        self.max_dist = 0.

        # Variables for plotting
        self.list_of_dist = []
        self.init_time = None
        self.list_of_times = []

    def run(self):
        self.device_range = DeviceRange()
        status = self.pozyx.doRanging(
            self.anchor_id, self.device_range, self.remote_id)
        if self.init_time is None:
            self.init_time = self.device_range.timestamp
        if status == POZYX_SUCCESS:
            # Update sampling rate if larger
            if self.prev_time is None:
                self.prev_time = time.time()
            else:
                curr_range_rate = 1 / (time.time() - self.prev_time) # in Hz
                if self.max_rate is None:
                    self.max_rate = curr_range_rate
                elif curr_range_rate > self.max_rate:
                    self.max_rate = curr_range_rate
            # Append distance and correlated time measurements
            print("Distance(m):",self.device_range.distance/1000)
            if self.device_range.distance > self.max_dist:
                self.max_dist = self.device_range.distance
            self.list_of_times.append(self.device_range.timestamp-self.init_time)
            self.list_of_dist.append(self.device_range.distance)
        else:
            error_code = SingleRegister()
            status = self.pozyx.getErrorCode(error_code)
            if status == POZYX_SUCCESS:
                print("ERROR Ranging, local %s" %
                    self.pozyx.getErrorMessage(error_code))
            else:
                print("ERROR Ranging, couldn't retrieve local error")

    def plot(self):
        print("Plotting...")
        distance_values = np.asarray(self.list_of_dist)
        t = np.asarray(self.list_of_times)

        # Plot Results
        fig = plt.figure(1)
        plt.plot(t/1000,distance_values/1000)
        plt.title("1 Tag to 1 Anchor: Max Distance Test")
        plt.xlabel("Time (s)")
        plt.ylabel("Distance (m)")
        plt.text(1,1,'Max Sampling Rate: {}'.format(round(self.max_rate,2)))
        plt.show()

        # Get and Print UWB Settings
        curr_master_uwb_settings = UWBSettings()
        curr_tag_uwb_settings = UWBSettings()
        status = self.pozyx.getUWBSettings(curr_master_uwb_settings)
        status &= self.pozyx.getUWBSettings(curr_tag_uwb_settings,self.remote_id)
        if status == POZYX_SUCCESS:
            print('Master UWB Settings => Channel: {}, Bitrate: {}, PRF: {}, Plen: {}, Gain(dB): {}'.\
                format(curr_master_uwb_settings.channel,UWBMapping.BITRATES[curr_master_uwb_settings.bitrate],\
                    UWBMapping.PRFS[curr_master_uwb_settings.prf],UWBMapping.PREAMBLE_LENGTHS[curr_master_uwb_settings.plen],\
                    curr_master_uwb_settings.gain_db))
            print('Tag UWB Settings => Channel: {}, Bitrate: {}, PRF: {}, Plen: {}, Gain(dB): {}'.\
                format(curr_tag_uwb_settings.channel,UWBMapping.BITRATES[curr_tag_uwb_settings.bitrate],\
                    UWBMapping.PRFS[curr_tag_uwb_settings.prf],UWBMapping.PREAMBLE_LENGTHS[curr_tag_uwb_settings.plen],\
                    curr_tag_uwb_settings.gain_db))
        else:
            print("UWB Setting Retrieval Failed!")
        print("Max Sampling Rate(Hz):",round(self.max_rate,2))
        print("Max Distance(m):",round(self.max_dist/1000,2))


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
    pozyx.addDevice(DeviceCoordinates(remote_id,1,Coordinates(0,0,0)))
    # WORKING SETTINGS: UWBSettings(channel=5,bitrate=0,prf=2,plen=0x08,gain_db=11.5)
    # uwb_settings = UWBSettings(channel=5,bitrate=0,prf=2,plen=0x08,gain_db=11.5)
    # uwb_settings = UWBSettings(channel=2,bitrate=0,prf=2,plen=0x08,gain_db=15.5)
    # status = pozyx.setUWBSettings(uwb_settings=uwb_settings,remote_id=remote_id)
    # status &= pozyx.setUWBSettings(uwb_settings=uwb_settings)

    status = pozyx.setUWBChannel(2,remote_id=remote_id)
    status &= pozyx.setUWBChannel(2)

    # Get and Print UWB Settings
    curr_master_uwb_settings = UWBSettings()
    curr_tag_uwb_settings = UWBSettings()
    status &= pozyx.getUWBSettings(curr_master_uwb_settings)
    status &= pozyx.getUWBSettings(curr_tag_uwb_settings,remote_id)
    if status == POZYX_SUCCESS:
        print('Master UWB Settings => Channel: {}, Bitrate: {}, PRF: {}, Plen: {}, Gain(dB): {}'.\
            format(curr_master_uwb_settings.channel,UWBMapping.BITRATES[curr_master_uwb_settings.bitrate],\
                UWBMapping.PRFS[curr_master_uwb_settings.prf],UWBMapping.PREAMBLE_LENGTHS[curr_master_uwb_settings.plen],\
                curr_master_uwb_settings.gain_db))
        print('Tag UWB Settings => Channel: {}, Bitrate: {}, PRF: {}, Plen: {}, Gain(dB): {}'.\
            format(curr_tag_uwb_settings.channel,UWBMapping.BITRATES[curr_tag_uwb_settings.bitrate],\
                UWBMapping.PRFS[curr_tag_uwb_settings.prf],UWBMapping.PREAMBLE_LENGTHS[curr_tag_uwb_settings.plen],\
                curr_tag_uwb_settings.gain_db))
    else:
        print("UWB Setting Retrieval Failed!")
        quit()
    
    
    t2a = Tag2AnchorDistance(pozyx,remote_id,anchor1_id)
    try:
        while True:
            t2a.run()
    except KeyboardInterrupt:
        pass
    
    t2a.plot()