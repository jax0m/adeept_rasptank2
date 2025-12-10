#!/usr/bin/python3
# coding=utf-8
# File name   : setup.py
# Author      : Devin

import os

# Get current username and home directory
# This handles cases where the script is run with sudo or directly
username = os.popen("echo ${SUDO_USER:-$(who -m | awk '{ print $1 }')}")
user_home = os.popen('getent passwd %s | cut -d: -f 6'%username).readline().strip()         # home

# Get the absolute path of the current script
curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)

print("Repo detected as: " + thisPath)

# Function to replace a specific line in a file
# This function takes a file path, the prefix of the line to replace, and the new value
# It reads the file, replaces the line that starts with the specified prefix with the new value, and writes it back
# Returns True if successful, False otherwise
# The function handles exceptions and provides error messages
def replace_num(file, initial, new_num):
    newline = ""
    str_num = str(new_num)
    try:
        with open(file, "r") as f:
            for line in f.readlines():
                if line.strip().startswith(initial):
                    line = str_num + '\n'
                newline += line
        with open(file, "w") as f:
            f.writelines(newline)
        return True
    except Exception as e:
        print(f"Error updating {file}: {str(e)}")
        return False

# Function to validate if all expected lines are present in a file
# Takes a file path and a list of expected lines to check for
# Returns True if all lines are present in the file, False otherwise
# Handles exceptions gracefully
def validate_config(file, expected_lines):
    try:
        with open(file, "r") as f:
            content = f.read()
        return all(line in content for line in expected_lines)
    except:
        return False

# Function to check for the presence of the Raspberry Pi config file
# Checks both possible locations: /boot/config.txt and /boot/firmware/config.txt
# Returns the path of the first existing config file, or None if neither exists
# This function is used to determine which config file to modify
def check_config_file():
    # Check for both possible config file locations
    config_locations = ["/boot/config.txt", "/boot/firmware/config.txt"]
    
    # Try to find a valid config file
    config_path = None
    for path in config_locations:
        if os.path.exists(path):
            config_path = path
            break
    
    if not config_path:
        print("Error: Neither /boot/config.txt nor /boot/firmware/config.txt exists.")
        return None
    
    return config_path

# Function to enable I2C and start_x in the Raspberry Pi config file
# This function checks if the required lines are already present
# If not, it attempts to modify the config file to enable I2C and start_x
# Returns True if successful, False otherwise
# Includes safety checks and validation
def enable_i2c_and_start_x():
    config_path = check_config_file()
    if not config_path:
        return False
    
    # Check if we need to make changes
    required_lines = ["dtparam=i2c_arm=on", "start_x=1"]
    
    # First check if all required lines are already present
    if validate_config(config_path, required_lines):
        print("I2C and start_x are already enabled in the config file.")
        return True
    
    # Try to modify the file
    success = replace_num(config_path, '#dtparam=i2c_arm=on', 'dtparam=i2c_arm=on\nstart_x=1\n')
    
    if success:
        # Validate the changes were made
        if validate_config(config_path, required_lines):
            print("Successfully enabled I2C and start_x in the config file.")
            return True
        else:
            print("Warning: Changes may not have been applied correctly. Please check the config file manually.")
            return False
    else:
        print("Error updating boot config to enable i2c. Please try again.")
        return False

# Function to check the Raspberry Pi OS version from /etc/os-release
# Reads the VERSION_ID from /etc/os-release and returns it as an integer
# Returns 12 as default if there's an error reading the file
# Used to determine which set of pip commands to use based on the OS version    
def check_raspbain_version():
    try:
        with open('/etc/os-release', 'r') as f:
            for line in f:
                if line.startswith('VERSION_ID='):
                    version = line.strip().split('=')[1]
                    # Remove quotes if present
                    version = version.strip('"')
                    return int(version)
    except Exception as e:
        print(f'Error reading /etc/os-release: {str(e)}')
        return 12  # Default to 12 if there's an error

# Update the package list
print("Updating apt-get package list(s)")
os.system("sudo apt-get update")

# Main execution
# List of commands to install required packages using apt-get
# These commands are run multiple times (up to 3 times) to ensure they succeed
# The script uses a mark variable to track if any command failed
# If a command fails, the mark is set to 1, and the loop continues to the next iteration
# If all commands succeed in one iteration, the loop breaks
# This is a safety measure to ensure that the installation process completes successfully
commands_apt = [
"sudo apt-get install -y python3-gpiozero",
"sudo apt-get install -y python3-pigpio",
"sudo apt-get install -y python3-opencv",
"sudo apt-get install -y python3-pyqt5",
"sudo apt-get install -y python3-opengl",
"sudo apt-get install -y python3-picamera2",
"sudo apt-get install -y python3-picamera2 --no-install-recommends",
"sudo apt-get install -y python3-opencv",
"sudo apt-get install -y opencv-data",
"sudo apt-get install -y python3-pyaudio"
]
mark_apt = 0
for x in range(3):
    for command in commands_apt:
        if os.system(command) != 0:
            print("Error running installation step apt")
            mark_apt = 1
    if mark_apt == 0:
        break

# List of commands to install required Python packages using pip3
# The script uses different sets of commands based on the Raspberry Pi OS version
# For OS version <= 11, it uses commands_pip_1
# For OS version > 11, it uses commands_pip_2
# This is likely due to changes in Python package management between different OS versions
# The commands are run multiple times (up to 3 times) to ensure they succeed
# The script uses a mark variable to track if any command failed
# If a command fails, the mark is set to 1, and the loop continues to the next iteration
# If all commands succeed in one iteration, the loop breaks
# This is a safety measure to ensure that the installation process completes successfully
commands_pip_1 = [
"sudo pip install adafruit-circuitpython-motor",
"sudo pip install adafruit-circuitpython-pca9685",
"sudo pip install flask",
"sudo pip install flask_cors",
"sudo pip install numpy",
"sudo pip install pyzmq",
"sudo pip install imutils",
"sudo pip install zmq",
"sudo pip install pybase64",
"sudo pip install psutil",
"sudo pip install websockets==13.0",
"sudo pip install rpi_ws281x",
"sudo pip install adafruit-circuitpython-ads7830"
]
commands_pip_2 = [
"sudo pip install --break-system-packages adafruit-circuitpython-motor",
"sudo pip install --break-system-packages adafruit-circuitpython-pca9685",
"sudo pip install --break-system-packages flask",
"sudo pip install --break-system-packages flask_cors",
"sudo pip install --break-system-packages numpy",
"sudo pip install --break-system-packages pyzmq",
"sudo pip install --break-system-packages imutils",
"sudo pip install --break-system-packages zmq",
"sudo pip install --break-system-packages pybase64",
"sudo pip install --break-system-packages psutil",
"sudo pip install --break-system-packages websockets==13.0",
"sudo pip install --break-system-packages rpi_ws281x",
"sudo pip install --break-system-packages adafruit-circuitpython-ads7830"
]
mark_pip = 0
OS_version = check_raspbain_version()
if OS_version <= 11:
    for x in range(3):
        for command in commands_pip_1:
            if os.system(command) != 0:
                print("Error running installation step pip")
                mark_pip = 1
        if mark_pip == 0:
            break
else:
    for x in range(3):
        for command in commands_pip_2:
            if os.system(command) != 0:
                print("Error running installation step pip")
                mark_pip = 1
        if mark_pip == 0:
            break

# List of commands to install create_ap, a tool for creating Wi-Fi hotspots
# The commands are run multiple times (up to 3 times) to ensure they succeed
# The script uses a mark variable to track if any command failed
# If a command fails, the mark is set to 1, and the loop continues to the next iteration
# If all commands succeed in one iteration, the loop breaks
# This is a safety measure to ensure that the installation process completes successfully
commands_3 = [
    "cd ~",
    "sudo git clone https://github.com/oblique/create_ap",
    "cd create_ap && sudo make install",
    "sudo apt-get install -y util-linux procps hostapd iproute2 iw haveged dnsmasq"
]
mark_3 = 0
for x in range(3):
    for command in commands_3:
        if os.system(command) != 0:
            print("Error running installation step 3")
            mark_2 = 1
    if mark_3 == 0:
        break

# Enable I2C and start_x with safety checks
# This function enables the I2C interface and start_x setting in the Raspberry Pi config file
# These settings are necessary for the Robot HAT to function properly
# The function includes safety checks to ensure the config file exists and the changes are applied correctly
if enable_i2c_and_start_x():
    print("I2C and start_x enabled successfully.")
else:
    print("Failed to enable I2C and start_x. Please check the config file manually.")

# Create a startup script that will run when the Raspberry Pi boots
# The script will run the web server program after a 5-second delay
# This ensures that all system services are ready before the program starts
try:
    os.system("touch ~/startup.sh")
    with open("~/startup.sh",'w') as file_to_write:
        file_to_write.write("#!/bin/sh\nsleep 5\nsudo python3 " + thisPath + "/web/webServer_HAT_V3.1.py")
    os.system("sudo chmod 777 ~/startup.sh")
except Exception as e:
    print(f"Error creating startup.sh: {str(e)}")

# Check if /etc/rc.local exists
# This file is used to run programs at boot time on older versions of Raspberry Pi OS
# If it doesn't exist, the script prompts the user to create it
# If it does exist, the script adds the startup script to it
if not os.path.exists("/etc/rc.local"):
    print('/etc/rc.local does not exist. It is required to run the program when the raspberry pi starts. \nHowever it is not required for function. \nWould you like to create a /etc/rc.local/ file (recommended)?')
    if input('(y/n): ').strip().lower() == "y":
        os.system("sudo touch /etc/rc.local")
        os.system("sudo chown root:root /etc/rc.local")
        os.system("sudo chmod 755 /etc/rc.local")
        try:
            with open("/etc/rc.local", 'w') as file_to_write:
                file_to_write.write('#!/bin/sh -e\n/' + user_home + '/startup.sh start\nexit 0')
        except Exception as e:
            print(f'Error: writing /etc/rc.local/ failed: {str(e)}')
    else:
        print("Program setup without /etc/rc.local complete. \nNote: you will have to run startup.sh manually to set servos for mechanical assembly.")
else: #there is /etc/rc.local
    try:
        replace_num('/etc/rc.local','fi','fi\n/'+ user_home +'/startup.sh start')
        print('/etc/rc.local setup complete. After turning the Raspberry Pi on again, the Raspberry Pi will automatically run the program to set the servos port signal to turn the servos to the middle position, which is convenient for mechanical assembly.')
    except Exception as e:
        print(f'Error adding to /etc/rc.local: {str(e)}')

# Display a completion message to the user
print('The program in Raspberry Pi has been installed, disconnected and restarted. \nYou can now power off the Raspberry Pi to install the camera and driver board (Robot HAT). \nAfter turning on again, the Raspberry Pi will automatically run the program to set the servos port signal to turn the servos to the middle position, which is convenient for mechanical assembly.')

# Prompt the user to confirm if they want to reboot
confirm_reboot = input("Would you like to reboot the Raspberry Pi now? (y/n): ").strip().lower()
if confirm_reboot == 'y':
    print('Rebooting...')
    os.system("sudo reboot")
else:
    print('Reboot cancelled. You may need to restart manually to complete the setup.')
