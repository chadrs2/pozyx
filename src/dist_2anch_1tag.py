#!/usr/bin/python3

from pypozyx import *
import matplotlib.pyplot as plt
import numpy as np
import time

from pypozyx.lib import Device

class Tag2AnchorsDistance():
    def __init__(self,pozyx,remote_id,anchor1_id,anchor2_id):        
        self.pozyx = pozyx

        # Clear all anchors connected to remote id tag
        self.pozyx.clearDevices(remote_id=remote_id)
        
        # Add anchor(s) to remote device
        anchor1 = DeviceCoordinates(anchor1_id,0,Coordinates(0,0,0))
        anchor2 = DeviceCoordinates(anchor2_id,0,Coordinates(3000,0,0)) #offset anchors by 1.5 meters
        self.pozyx.addDevice(anchor1,remote_id)
        self.pozyx.addDevice(anchor2,remote_id)

        # State Variables
        self.remote_id = remote_id
        self.anchor1_id = anchor1_id
        self.anchor1 = anchor1
        self.anchor2_id = anchor2_id
        self.anchor2 = anchor2
        self.device_range = DeviceRange()
        self.prev_time = None
        self.max_rate = None
        self.max_dist = 0.

        # Variables for plotting
        self.list_of_dist1 = []
        self.list_of_dist2 = []
        self.init_time = None
        self.list_of_times1 = []
        self.list_of_times2 = []

    def run(self):
        self.device1_range = DeviceRange()
        status = self.pozyx.doRanging(
            self.anchor1_id, self.device1_range, self.remote_id)
        self.device2_range = DeviceRange()
        status &= self.pozyx.doRanging(
            self.anchor2_id, self.device2_range, self.remote_id)
        if self.init_time is None:
            self.init_time = self.device1_range.timestamp
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
            print('Distance(m) from: Anchor 1={}, Anchor 2={}'.format(self.device1_range.distance/1000,self.device2_range.distance/1000))
            if self.device1_range.distance > self.max_dist:
                self.max_dist = self.device1_range.distance
            if self.device2_range.distance > self.max_dist:
                self.max_dist = self.device2_range.distance
            self.list_of_times1.append(self.device1_range.timestamp-self.init_time)
            self.list_of_times2.append(self.device2_range.timestamp-self.init_time)
            self.list_of_dist1.append(self.device1_range.distance)
            self.list_of_dist2.append(self.device2_range.distance)
        else:
            error_code = SingleRegister()
            status = self.pozyx.getErrorCode(error_code)
            if status == POZYX_SUCCESS:
                print("ERROR Ranging, local %s" %
                    self.pozyx.getErrorMessage(error_code))
            else:
                print("ERROR Ranging, couldn't retrieve local error")

    def plot(self):
        print()
        print("Plotting...")
        distance_values1 = np.asarray(self.list_of_dist1)
        distance_values2 = np.asarray(self.list_of_dist2)
        t1 = np.asarray(self.list_of_times1)
        t2 = np.asarray(self.list_of_times2)

        # Plot Results
        fig = plt.figure(1)
        plt.plot(t1/1000,distance_values1/1000,label='Distance to Anchor 1')
        plt.plot(t2/1000,distance_values2/1000,label='Distance to Anchor 2')
        plt.title("1 Tag to 2 Anchors: Max Distance Test")
        plt.xlabel("Time (s)")
        plt.ylabel("Distance (m)")
        plt.text(1,1,'Max Sampling Rate: {}'.format(round(self.max_rate,2)))
        plt.legend()
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
    remote_id = 0x7607            # remote tag device network ID
    anchor1_id = 0x7612                 # anchor 1 device network ID
    anchor2_id = 0x7653                 # anchor 2 device network ID
    
    pozyx = PozyxSerial(serial_port)

    # dd = DeviceDetails()
    # pozyx.getDeviceDetails(dd)
    # print("Master Details:",dd)
    # dd = DeviceDetails()
    # pozyx.getDeviceDetails(dd,remote_id)
    # print("Tag Details:",dd)

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
    # WORKING SETTINGS: UWBSettings(channel=5,bitrate=0,prf=2,plen=0x08,gain_db=11.5)
    # uwb_settings = UWBSettings(channel=5,bitrate=0,prf=2,plen=0x08,gain_db=11.5)
    uwb_settings = UWBSettings(channel=5,bitrate=0,prf=2,plen=0x08,gain_db=11.5)
    status = pozyx.setUWBSettings(uwb_settings=uwb_settings,remote_id=remote_id)
    status &= pozyx.setUWBSettings(uwb_settings=uwb_settings)
    # status = pozyx.setUWBChannel(2,remote_id=remote_id)
    # status = pozyx.setUWBChannel(2)
    # status = pozyx.clearConfiguration()
    # status &= pozyx.clearConfiguration(remote_id)
    # # status = POZYX_SUCCESS
    # if status == POZYX_SUCCESS:
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
    # else:
    #     print("UWB Settings Setting Failed!")
    #     quit()
    
    
    t2a = Tag2AnchorsDistance(pozyx,remote_id,anchor1_id,anchor2_id)
    try:
        while True:
            t2a.run()
    except KeyboardInterrupt:
        pass
    
    t2a.plot()