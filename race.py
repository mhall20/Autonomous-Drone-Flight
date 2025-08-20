from Marty_Module import Pihawk
from dronekit import VehicleMode, LocationGlobalRelative
import time

def read_coordinates_from_file(file_path):
    """
    Reads coordinates from a text file and converts them into an array.
    Each line in the file should be in the format: "lat, lon".
    """
    coordinates = []
    with open(file_path, "r") as file:
        for line in file:
            lat, lon = map(float, line.strip().split(","))
            coordinates.append((lat, lon))
    return coordinates

if __name__ == "__main__":
    file_path = "coordinates.txt"
    coordinates_array = read_coordinates_from_file(file_path)

    # Create a Pihawk object
    marty = Pihawk()

    marty.arm()
    marty.takeoff(10)

    try:
        # Loop through each coordinate and fly to it
        while coordinates_array:
            coord = coordinates_array[0]  # Peek at the first coordinate without removing it
            lat, lon = coord
            print(f"Flying to Latitude: {lat}, Longitude: {lon}")
            marty.fly_to_location(lat, lon, alt=None, speed=10)
            print(f"Reached Latitude: {lat}, Longitude: {lon}")
            marty.set_new_home()
            # Remove the coordinate only after reaching it
            coordinates_array.pop(0)

        marty.drone.mode = VehicleMode("LAND")
    except KeyboardInterrupt:
        print("\nFlight interrupted by user.")
    finally:
        marty.drone.mode = VehicleMode("LAND")
        time.sleep(20)
        # Ensure the drone is safely disconnected
        marty.drone.close()

