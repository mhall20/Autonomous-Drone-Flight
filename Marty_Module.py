import time
import math
import collections
import collections.abc
collections.MutableMapping = collections.abc.MutableMapping
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil

class Pihawk:
    def __init__(self, connection_string='/dev/ttyAMA0', baud=57600):
        self.drone = None
        try:
            print("Attempting to connect to drone...")
            self.drone = connect(connection_string, wait_ready=True, baud=baud)
            print("Battery voltage: ", self.drone.battery)

            self.drone.mode = VehicleMode("GUIDED")
            while self.drone.mode != "GUIDED":
                print("Waiting for drone to enter GUIDED mode...")
                time.sleep(1)
            print("Drone is in GUIDED mode.")
        except Exception as e:
            print(f"Error: {str(e)}")
            raise RuntimeError("Cannot connect to drone")

        self.cmds = self.drone.commands
        self.cmds.download()
        self.cmds.wait_ready()
        if not self.drone.home_location:
            print(" Waiting for home location ...")
        print ("Home Location: %s" % self.drone.home_location)
        self.drone.home_location=self.drone.location.global_frame

        self.flight = False

    def disconnect(self):
        self.close()

    def close(self):
        if self.drone:
            if self.drone.mode != "LAND":
                print("Landing...")
                self.land()
            if not self.drone.armed:
                print("Disarming...")
                self.disarm()
            self.drone.close()

    def set_new_home(self):
        self.drone.home_location=self.drone.location.global_frame
        print("New home location set to current location.")
        return

    def arm(self):
        print("Arming drone...")
        if not self.drone.is_armable:
            return self.drone.armed
        self.drone.armed = True
        while not self.drone.armed:
            print("Waiting for drone to arm...")
            time.sleep(1)
        print("Drone is armed.")
        return self.drone.armed
    
    def disarm(self):
        print("Disarming drone...")
        if self.drone == None:
            raise
        self.drone.armed = False
        while self.drone.armed:
            print("Waiting for drone to disarm...")
            time.sleep(1)
        return self.drone.armed
    
    def takeoff(self, takeoff_height=1):
        print("Taking off...")
        height = 0
        count = 0
        if height > 10:
            print("Capping takeoff height to 10m")
            takeoff_height = 10

        self.drone.simple_takeoff(takeoff_height)
        timeout = takeoff_height * 5
        while height < 0.95 * takeoff_height and count < timeout:
            height = self.drone.location.global_relative_frame.alt
            print(f"Drone is now at height: %sm... %s" % (height, count))
            time.sleep(1)
            count += 1
        return height
    
    def land(self):

        while self.flight:
            print("Still flying, cannot land")
            time.sleep(1)

        print("Landing drone...")
        self.drone.mode = VehicleMode("LAND")
        count = 1
        while self.drone.mode != "LAND" and count < 30:
            print("Waiting for drone to land...")
            time.sleep(1)
            count += 1
        return self.drone.mode
    
    def fly_to_location(self, lat, lon, alt=None, speed=5):
        """
        Fly the drone to a specific latitude, longitude, and altitude.
        Blocks execution until the drone reaches the target location.
        """
        if alt is None:
            alt = self.drone.location.global_relative_frame.alt

        location = LocationGlobalRelative(lat, lon, alt)

        print(f"Flying to location: {location}")
        self.drone.simple_goto(location, groundspeed=speed)

        self.flight = True

        while self.flight:
            current_location = self.drone.location.global_relative_frame
            distance_to_target = self.get_distance(current_location, location)
            print(f"Distance to target: {distance_to_target:.2f} meters")

            if distance_to_target <= 1.0:  # Stop when within 1 meter of the target
                print("Reached target location.")
                self.flight = False
                break

            time.sleep(1)
    
    # meters
    def get_distance(self, location1, location2):
        dlat = location2.lat - location1.lat
        dlon = location2.lon - location1.lon
        return math.sqrt((dlat * 1.113195e5)**2 + (dlon * 1.113195e5)**2)