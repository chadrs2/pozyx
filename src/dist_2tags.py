#!/usr/bin/python3

#from pypozyx import PozyxSerial, get_first_pozyx_serial_port, POZYX_SUCCESS, SingleRegister, EulerAngles, Acceleration
from pypozyx import *
import matplotlib.pyplot as plt
import numpy as np
import time

from pypozyx.lib import Device

class TagsDistance():
    def __init__(self,pozyx,remote_id):        
        self.pozyx = pozyx

        # State Variables
        self.remote_id = remote_id
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
            destination_id=self.remote_id, device_range=self.device_range, remote_id=None)
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
            print("Distance(m):",self.device_range.distance/1000,"at",(self.device_range.timestamp-self.init_time)/1000,"sec")
            if self.device_range.distance > self.max_dist:
                self.max_dist = self.device_range.distance
            if self.device_range.timestamp - self.init_time > 0. and self.device_range.distance/1000 < 200.:
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
        # plt.plot(t/1000,distance_values/1000)
        plt.scatter(t/1000,distance_values/1000,marker=".")
        plt.title("2 Tags: Max Distance Test")
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

    def stats(self):
        print("Standard Deviation of 100 measurements @ 100m:",np.std(np.asarray(self.list_of_dist)/1000))
        print("Variance of 100 measurements @ 100m:",np.var(np.asarray(self.list_of_dist)/1000))
        print("Mean of 100 measurements @ 100m:",np.mean(np.asarray(self.list_of_dist)/1000))


if __name__ == "__main__":
    # Master Tag serial port
    serial_port = get_first_pozyx_serial_port()
    if serial_port is None:
        print("No Pozyx connected. Check your USB cable or your driver!")
        quit()
    
    # Device ID Config
    remote_id = 0x7607                 # remote tag device network ID
    
    pozyx = PozyxSerial(serial_port)

    # # Configure Network
    pozyx.clearDevices(remote_id)
    pozyx.clearDevices()
    pozyx.addDevice(DeviceCoordinates(remote_id,1,Coordinates(0,0,0)))
    # pozyx.saveNetwork()
    
    # Change Settings    
    # uwb_settings = UWBSettings(channel=5,bitrate=0,prf=2,plen=0x08,gain_db=11.5)
    uwb_settings = UWBSettings(channel=2,bitrate=0,prf=2,plen=0x0C,gain_db=15.5)
    status = pozyx.setUWBSettings(uwb_settings=uwb_settings,remote_id=remote_id)
    status &= pozyx.setUWBSettings(uwb_settings=uwb_settings)
    #pozyx.saveUWBSettings()
    #pozyx.saveUWBSettings(remote_id)

    # Get and Print UWB Settings
    curr_master_uwb_settings = UWBSettings()
    curr_tag_uwb_settings = UWBSettings()
    status = pozyx.getUWBSettings(curr_master_uwb_settings)
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
    
    
    td = TagsDistance(pozyx,remote_id)
    try:
        while True:
            td.run()
            # print(len(td.list_of_dist))
            # if len(td.list_of_dist) == 100:
            #     td.stats()
            #     break
            # time.sleep(1/15)
    except KeyboardInterrupt:
        pass
    
    # Save Variables:
    '''
    import pickle

    f = open('store.pckl', 'wb')
    pickle.dump(obj, f)
    f.close()

    f = open('store.pckl', 'rb')
    obj = pickle.load(f)
    f.close()
    '''
    td.plot()