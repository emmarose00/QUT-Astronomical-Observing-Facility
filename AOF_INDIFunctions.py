#import indi_client
#import time

from AOF_SendCommand import send_command, send_data

def extract_value_from_command(command, attribute):
    start_index = command.find(f"{attribute}=\"") + len(f"{attribute}=\"")
    end_index = command.find("\"", start_index)
    return command[start_index:end_index]

def move_filter(indi_command, current_filter_slot):
    # Extract the filter wheel command type
    filter_wheel_command = extract_value_from_command(indi_command, "Command")

    # Check the filter wheel command type
    if filter_wheel_command == "Goto":
        # Extract the target filter slot number
        target_filter_slot = extract_value_from_command(indi_command, "Slot")

        # Check if the filter slot number is within the range of 1 to 7
        if target_filter_slot.isdigit():
            target_filter_slot = int(target_filter_slot)
            if 1 <= target_filter_slot <= 7:
                # Check if the filter wheel is already in the target position
                if current_filter_slot == target_filter_slot:
                    print(f"Filter wheel is already in Slot {target_filter_slot}. No need to move.\n")
                    return current_filter_slot

                print("Sending command to move filter wheel...")
                send_command(indi_command)
                print(f"Filter wheel moved to Slot {target_filter_slot}.\n")
                return target_filter_slot
            else:
                print("Invalid filter slot number. Please enter a number between 1 and 7.\n")
        else:
            print("Invalid filter slot number. Please enter a numeric value.\n")

    else:
        # Handle unknown filter wheel commands
        print("Unknown filter wheel command:", filter_wheel_command)

    return current_filter_slot

def move_dome(indi_command,dome_state,current_dome_position):

    # Determine if the command is to open or close the dome
    is_close_command = "DomeAz=\"0\" DomeAlt=\"0\"" in indi_command

    if is_close_command:
        print("Sending command to close observatory dome...")
    else:
        print("Sending command to move observatory dome...")

    # Extract target azimuth and altitude from the command
    target_azimuth = float(extract_value_from_command(indi_command, "DomeAz"))
    target_altitude = float(extract_value_from_command(indi_command, "DomeAlt"))

    if not is_close_command and (target_azimuth, target_altitude) == current_dome_position:
        print(f"Observatory dome is already at Azimuth: {target_azimuth}°, Altitude: {target_altitude}°.\n")
        return dome_state, current_dome_position


    # Send the INDI command to the dome controller
    if send_command(indi_command):

        if is_close_command:
            if dome_state == 1:
                print("Observatory dome is closing.\n")
                dome_state = 0
                current_dome_position = (0, 0)
            else:
                print("Observatory dome is already closed.\n")
        else:
            if dome_state == 0:
                print("Observatory dome is opening.\n")
                dome_state = 1
            else:
                print(f"Observatory dome has been moved to Azimuth: {target_azimuth}°, Altitude: {target_altitude}°.\n")
            current_dome_position = (target_azimuth, target_altitude)
    else:
        print("Failed to send command to move observatory dome. Please try again.\n")

    return True, dome_state, current_dome_position
    

def move_telescope(indi_command,dome_state,current_telescope_position):

    ra = extract_value_from_command(indi_command, "RA")
    dec = extract_value_from_command(indi_command, "Dec")

    # Check if the telescope is already at the target position
    if current_telescope_position == (ra, dec):
        print(f"Telescope is already at coordinates: RA {ra}, Dec {dec}.\n")
        return False, dome_state, current_telescope_position

    # Check if the dome is open
    if dome_state == 0:
        print("Dome is closed. Sending command to open dome...")
        # Check the weather conditions
        dome_open_command = "<indi><telescopeDomeDevice Dome=\"Dome\"><DomeCommand Command=\"Goto\" DomeAz=\"180\" DomeAlt=\"45\" /></telescopeDomeDevice></indi>"
        send_command(dome_open_command)
        dome_state = move_dome(dome_open_command, dome_state,(0.0, 0.0))
            
        # If the dome could not be opened, return False
        if dome_state == 0:
            print("Failed to open dome. Telescope movement aborted.\n")
            return False, dome_state, current_telescope_position
            
    
    # Print a message indicating that the command has been sent
    print("Sending command to move telescope...")

    # Send the INDI command to the telescope
    if send_command(indi_command):
        # Print a message indicating that the command has been sent
        print(f"Moved telescope to coordinates: RA {ra}, Dec {dec}.\n")
        return True, dome_state,(ra, dec)
    else:
        # Error
        print("Failed to send command to move telescope. Please try again.\n")
        return False, dome_state,current_telescope_position

def take_image(exposure_time,indi_command,dome_state):

    # Check if the dome is open
    if dome_state == 0:
        print("Dome is closed. Unable to take image.\n")
        return False
    
    print("Sending command to take_image...")
    send_command(indi_command)
    
    # Code to capture an image with the camera
    print(f"Taken image with exposure time {exposure_time} seconds.")

    # Code to capture an image with the camera
    print("Recieved FITS file, sending data...")
    image_data = "Simulated FITS file data"
    store_image(image_data)

def store_image(image_data):
    # Code to store the captured image
    print("Storing image...")
    send_data(image_data)
