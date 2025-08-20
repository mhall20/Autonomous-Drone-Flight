

import sys
import termios
import tty
from Marty_Module import Pihawk
import time

def get_keypress():
    """
    Captures a single keypress from the user without pressing Enter.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)  # Read 1 character
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def get_drone_coordinates_on_keypress():
    """
    Creates a Pihawk object and prints GPS coordinates whenever 'c' is pressed.
    """
    print("Creating Pihawk drone object...")
    marty = Pihawk()

    # Wait until GPS fix is available
    while not marty.drone.location.global_frame.lat:
        print("Waiting for GPS fix...")
        time.sleep(1)

    print("\nConnected! Press 'c' to get current coordinates. Press 'q' to quit.\n")

    coordinates = []

    try:
        while True:
            key = get_keypress()
            if key.lower() == 'c':
                location = marty.drone.location.global_frame
                lat = location.lat
                lon = location.lon
                alt = location.alt
                print(f"\nLatitude: {lat}")
                print(f"Longitude: {lon}")
                print(f"Altitude: {alt} meters\n")
                coordinates.append((lat, lon))
            elif key.lower() == 'q':
                print("Quitting...")
                break
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        with open("coordinates.txt", "w") as f:
            for coord in coordinates:
                f.write(f"{coord[0]}, {coord[1]}\n")
        marty.drone.close()

if __name__ == "__main__":
    get_drone_coordinates_on_keypress()
