#!/usr/bin/python3

#from pypozyx import PozyxSerial, get_first_pozyx_serial_port, POZYX_SUCCESS, SingleRegister, EulerAngles, Acceleration
from pypozyx import *
import matplotlib.pyplot as plt
import numpy as np

class Tag2AnchorDistance():
    def __init__(self,pozyx,remote_id,anchor_id):        
        self.pozyx = pozyx

        # Clear all anchors connected to remote id tag
        self.pozyx.clearDevices(remote_id=remote_id)
        
        # Add anchor(s) to remote device
        anchor1 = DeviceCoordinates(anchor_id,1,Coordinates(0,0,0))
        self.pozyx.addDevice(anchor1,remote_id)

        # State Variables
        self.remote_id = remote_id
        self.anchor_id = anchor_id
        self.anchor1 = anchor1
        self.device_range = DeviceRange()

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
            print("Distance:",self.device_range.distance/1000)
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
        plt.title("1 Tag to 1 Anchor: Outdoor Max Distance Test")
        plt.xlabel("Time (s)")
        plt.ylabel("Distance (m)")

        plt.show()


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
    '''
    ## Set the Pozyx's UWB settings.
    # If using this remotely, remember to change the local UWB settings as well
    # to make sure you are still able to communicate with the remote device.
    # Max Range :=: channel := 2(optimal); bitrate := 0(lower); plen := 2048(higher)
    # Max Rate :=: channel := 7(high); bitrate := 2(higher); plen := 64(lower)  
    uwb_settings = UWBSettings(channel=5, bitrate=1, prf=2, plen=0x08, gain_db=25.0)
    pozyx.setUWBSettings(self, uwb_settings, remote_id=None, save_to_flash=False):

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
    
    
    t2a = Tag2AnchorDistance(pozyx,remote_id,anchor1_id)
    try:
        while True:
            t2a.run()
    except KeyboardInterrupt:
        pass
    
    t2a.plot()    