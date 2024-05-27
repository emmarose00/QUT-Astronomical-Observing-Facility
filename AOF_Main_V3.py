#import indi_client
#import time

from AOF_INDIFunctions import move_telescope, take_image, store_image, move_dome, move_filter
from AOF_SendCommand import send_command

def update_weather():
    # Function to retrieve data from the weather station hardware

    while True:
        print("Enter weather data for simulation:")
        rain_input = input("Is it raining? (True/False): ").lower()
        if rain_input == 'true' or rain_input == 'false':
            rain = rain_input == 'true'
            break
        else:
            print("Invalid input. Please enter either 'True' or 'False'.\n")

    while True:
        wind_speed_input = input("Wind speed (in km/h): ")
        if wind_speed_input.isdigit():
            wind_speed = float(wind_speed_input)
            break
        else:
            print("Invalid input. Please enter a numeric value for wind speed.\n")

    while True:
        humidity_input = input("Humidity (in percentage): ")
        if humidity_input.isdigit():
            humidity = float(humidity_input)
            break
        else:
            print("Invalid input. Please enter a numeric value for humidity.\n")

    while True:
        cloudy_input = input("Is it cloudy? (True/False): ").lower()
        if cloudy_input == 'true' or cloudy_input == 'false':
            cloudy = cloudy_input == 'true'
            break
        else:
            print("Invalid input. Please enter either 'True' or 'False'.\n")

    weather_data = {
        'rain': rain,
        'wind_speed': wind_speed,
        'humidity': humidity,
        'cloudy': cloudy
    }
    
    return weather_data

def check_weather(weather_data, dome_state, current_dome_position):
    
    # weather station data retrieval every 10 minutes
    #time.sleep(600)
    indi_command_close_dome = "<indi><telescopeDomeDevice Dome=\"Dome\"><DomeCommand Command=\"Goto\" DomeAz=\"0\" DomeAlt=\"0\" /></telescopeDomeDevice></indi>"


    # extract relevant weather parameters
    cloudy = weather_data.get('cloudy', None)
    humidity = weather_data.get('humidity', None)
    rain = weather_data.get('rain', False)
    wind_speed = weather_data.get('wind_speed', None)

    # variables
    threshold_wind_speed = 30 #km/h
    threshold_humidity = 80 # in %

    # Check weather conditions
    if rain:
        print("It's raining. Observations paused.")
        # Code to pause observations or close dome, etc.

        if dome_state:
            #Close dome
            send_command(indi_command_close_dome)
            print("Observatory dome is closing.\n")
            dome_state = 0;
            current_dome_position = (0.0, 0.0) 
            
        return False, dome_state, current_dome_position
    elif cloudy:
        print("It's cloudy. Observations paused.")
        # Code to pause observations or close dome, etc.

        if dome_state:
            #Close dome
            send_command(indi_command_close_dome)
            print("Observatory dome is closing.\n")
            dome_state = 0;
            current_dome_position = (0.0, 0.0) 
            
        return False, dome_state, current_dome_position
        
    elif wind_speed > threshold_wind_speed:
        print("It's too windy for observations. Observations paused.")
        # Code to pause observations or close dome, etc.

        if dome_state:
            #Close dome
            send_command(indi_command_close_dome)
            print("Observatory dome is closing.\n")
            dome_state = 0;
            current_dome_position = (0.0, 0.0)
            
        return False, dome_state, current_dome_position
    elif humidity > threshold_humidity:
        print("It's too humid for observations. Observations paused.")
        # Code to pause observations or close dome, etc.

        if dome_state:
            #Close dome
            send_command(indi_command_close_dome)
            print("Observatory dome is closing.\n")
            dome_state = 0;
            current_dome_position = (0.0, 0.0)
            
        return False, dome_state, current_dome_position
    else:
        print("Weather is good. Observations can proceed.\n")
        return True, dome_state, current_dome_position


def extract_value_from_command(command, attribute):
    start_index = command.find(f"{attribute}=\"") + len(f"{attribute}=\"")
    end_index = command.find("\"", start_index)
    return command[start_index:end_index]

def process_indi_command(indi_command,dome_state, current_dome_position, current_telescope_position, exposure_time, current_filter_position):
    # Check the INDI command
    if "DomeCommand Command=\"Goto\"" in indi_command:
        success, dome_state, current_dome_position = move_dome(indi_command,dome_state,current_dome_position)
    elif "TelescopeCommand Command=\"Goto\"" in indi_command:
        success, dome_state, current_telescope_position = move_telescope(indi_command,dome_state,current_telescope_position)
    elif "CameraCommand Command=\"TakeImage\"" in indi_command:
        take_image(exposure_time,indi_command, dome_state)
    elif "FilterWheelCommand" in indi_command:
        current_filter_position = move_filter(indi_command,current_filter_position)
    return dome_state, current_dome_position, current_telescope_position, current_filter_position


def main():

    #Simulation Values
    dome_state = 0; # 0=closed, 1=open

    # replace weather_data with actual fetched data from the weather station
    weather_data = {
        'humidity': 50,     # example humidity data in percentage
        'rain': False,      # example rain data (True if raining, False otherwise)
        'wind_speed': 10,   # example wind speed data in km/h
        'cloudy': False     # example cloud data (True if cloudy, False otherwise)
    }


    # Variables
    exposure_time = 10;

    current_dome_position = (0.0, 0.0)  # Initial dome position
    current_telescope_position = {'RA': '', 'Dec': ''}  # Initial telescope position
    current_filter_position = 1
  
    
    while True:
        # Update weather data
        weather_data = update_weather()

        # Replace this with actual code to receive INDI commands
        new_indi_command = input("\nEnter new INDI command (or 'exit' to quit): ")

        if new_indi_command.lower() == 'exit':
            break  # Exit the loop if 'exit' command is received


        # Check weather conditions
        weather_ok, dome_state, current_dome_position = check_weather(weather_data, dome_state, current_dome_position)

        if weather_ok:
            # Process the new INDI command
            dome_state, current_dome_position, current_telescope_position, current_filter_position = process_indi_command(new_indi_command, dome_state, current_dome_position, current_telescope_position, exposure_time, current_filter_position)


if __name__ == "__main__":
    main()
