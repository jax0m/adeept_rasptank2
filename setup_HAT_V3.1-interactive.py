#!/usr/bin/python3
# File name   : setup.py
# Author      : Devin

import os
import argparse
import subprocess
from typing import Dict, List, Optional, Any

# Get current username and home directory
# This handles cases where the script is run with sudo or directly
username = os.popen("echo ${SUDO_USER:-$(who -m | awk '{ print $1 }')}").read().strip()
user_home = (
    os.popen("getent passwd %s | cut -d: -f 6" % username).readline().strip()
)  # home

# Get the absolute path of the current script
curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)

print("Repo detected as: " + thisPath)

# Add argparse for command-line arguments
parser = argparse.ArgumentParser(description="Raspberry Pi Robot HAT Setup Script")
parser.add_argument(
    "--auto", action="store_true", help="Run in automated mode without user prompts"
)
args = parser.parse_args()

auto_mode = args.auto


# Function to check if a package is installed via APT
def is_apt_package_installed(package: str) -> bool:
    try:
        result = subprocess.run(["dpkg", "-l", package], capture_output=True, text=True)
        return "ii" in result.stdout
    except Exception as e:
        print(f"Error checking APT package: {str(e)}")
        return False


# Function to check if a pip package is installed
def is_pip_package_installed(package: str) -> bool:
    try:
        result = subprocess.run(["pip3", "list"], capture_output=True, text=True)
        return package in result.stdout
    except Exception as e:
        print(f"Error checking PIP package: {str(e)}")
        return False


# Function to replace a specific line in a file
def replace_num(file: str, initial: str, new_num: str) -> bool:
    newline = ""
    try:
        with open(file) as f:
            for line in f.readlines():
                if line.strip().startswith(initial):
                    line = new_num + "\n"
                newline += line
        with open(file, "w") as f:
            f.writelines(newline)
        return True
    except Exception as e:
        print(f"Error updating {file}: {str(e)}")
        return False


# Function to validate if all expected lines are present in a file
def validate_config(file: str, expected_lines: List[str]) -> bool:
    try:
        with open(file) as f:
            content = f.read()
        return all(line in content for line in expected_lines)
    except Exception:
        return False


# Function to check for the presence of the Raspberry Pi config file
def check_config_file() -> Optional[str]:
    config_locations = ["/boot/config.txt", "/boot/firmware/config.txt"]
    config_path = None
    for path in config_locations:
        if os.path.exists(path):
            config_path = path
    if not config_path:
        print("Error: Neither /boot/config.txt nor /boot/firmware/config.txt exists.")
        return None
    return config_path


# Function to enable I2C and start_x in the Raspberry Pi config file
def enable_i2c_and_start_x() -> bool:
    config_path = check_config_file()
    if not config_path:
        return False

    required_lines = ["dtparam=i2c_arm=on", "start_x=1"]

    # Check if we need to make changes
    if validate_config(config_path, required_lines):
        print("I2C and start_x are already enabled in the config file.")
        return True

    # Try to modify the file
    success = replace_num(
        config_path, "#dtparam=i2c_arm=on", "dtparam=i2c_arm=on\nstart_x=1\n"
    )

    if success:
        # Validate the changes were made
        if validate_config(config_path, required_lines):
            print("Successfully enabled I2C and start_x in the config file.")
            return True
        else:
            print(
                "Warning: Changes may not have been applied correctly. Please check the config file manually."
            )
            return False
    else:
        print("Error updating boot config to enable i2c. Please try again.")
        return False


# Function to check the Raspberry Pi OS version from /etc/os-release
def check_raspbain_version() -> int:
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if line.startswith("VERSION_ID="):
                    version = line.strip().split("=")[1]
                    version = version.strip('"')
                    return int(version)
    except Exception as e:
        print(f"Error reading /etc/os-release: {str(e)}")
        return 12  # Default to 12 if there's an error
    return 12  # Ensure function returns a value


# Function to get user confirmation
def get_user_confirmation(message: str) -> bool:
    if auto_mode:
        return True

    response = input(f"{message} (y/n): ").strip().lower()
    return response == "y"


# Update the package list
print("Updating apt-get package list(s)")
os.system("sudo apt-get update")

# Track installation results
installation_results: Dict[str, Dict[str, List[Any]]] = {
    "apt": {"installed": [], "failed": []},
    "pip": {"installed": [], "failed": []},
    "other": {"installed": [], "failed": []},
}

# Main execution

# List of commands to install required packages using apt-get
commands_apt: List[str] = [
    "sudo apt-get install -y python3-gpiozero",
    "sudo apt-get install -y python3-pigpio",
    "sudo apt-get install -y python3-opencv",
    "sudo apt-get install -y python3-pyqt5",
    "sudo apt-get install -y python3-opengl",
    "sudo apt-get install -y python3-picamera2",
    "sudo apt-get install -y python3-picamera2 --no-install-recommends",
    "sudo apt-get install -y python3-opencv",
    "sudo apt-get install -y opencv-data",
    "sudo apt-get install -y python3-pyaudio",
]

# List of commands to install required Python packages using pip3
commands_pip_1: List[str] = [
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
    "sudo pip install adafruit-circuitpython-ads7830",
]

commands_pip_2: List[str] = [
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
    "sudo pip install --break-system-packages adafruit-circuitpython-ads7830",
]

# List of commands to install create_ap, a tool for creating Wi-Fi hotspots
commands_3: List[str] = [
    "cd ~",
    "sudo git clone https://github.com/oblique/create_ap",
    "cd create_ap && sudo make install",
    "sudo apt-get install -y util-linux procps hostapd iproute2 iw haveged dnsmasq",
]


# Function to install packages with proper package name handling
def install_package(package: str, package_type: str, install_cmd: str) -> bool:
    # Fix: Properly handle package name extraction
    if package_type == "apt" and is_apt_package_installed(package):
        print(f"  {package} is already installed (skipping)")
        return True
    elif package_type == "pip" and is_pip_package_installed(package):
        print(f"  {package} is already installed (skipping)")
        return True

    # Fix: Ensure proper prompt formatting
    if not get_user_confirmation(f"  Install {package}? "):
        print(f"  Skipping {package} installation")
        return False

    result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  Successfully installed {package}")
        installation_results[package_type]["installed"].append(package)
        return True
    else:
        print(f"  Failed to install {package}: {result.stderr}")
        installation_results[package_type]["failed"].append(package)
        return False


# Install APT packages
print("\nInstalling APT packages:")
for cmd in commands_apt:
    # Extract package name from command
    package = cmd.split(" ")[2]  # The third element is the package name
    if "install" in cmd:
        install_package(package, "apt", cmd)


# Install PIP packages based on OS version
print("\nInstalling PIP packages:")
OS_version = check_raspbain_version()
pip_commands: List[str] = commands_pip_1 if OS_version <= 11 else commands_pip_2

for cmd in pip_commands:
    # Extract package name from command
    package = cmd.split(" ")[3]  # The fourth element is the package name
    if "install" in cmd:
        install_package(package, "pip", cmd)


# Install other packages
print("\nInstalling other components:")
for cmd in commands_3:
    if "apt-get install" in cmd:
        # Extract packages from command
        packages = cmd.split(" ")[4:]
        for package in packages:
            if not get_user_confirmation(f"  Install {package}? "):
                continue
            if not install_package(package, "other", cmd):
                installation_results["other"]["failed"].append(package)
    else:
        if "git clone" in cmd or "make" in cmd:
            if not get_user_confirmation(f"  Install {cmd}? "):
                continue
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("  Successfully installed component")
                installation_results["other"]["installed"].append(cmd)
            else:
                print(f"  Failed to install: {result.stderr}")
                installation_results["other"]["failed"].append(cmd)


# Enable I2C and start_x with safety checks
print("\nConfiguring I2C and start_x...")
if get_user_confirmation("  Enable I2C and start_x? "):
    if enable_i2c_and_start_x():
        print("  I2C and start_x enabled successfully.")
    else:
        print(
            "  Failed to enable I2C and start_x. Please check the config file manually."
        )


# Create a systemd service file for startup
print("\nConfiguring startup service...")
if get_user_confirmation("  Set up startup service? "):
    try:
        service_file = "/etc/systemd/system/robot_hat_startup.service"
        with open(service_file, "w") as f:
            f.write("[Unit]\n")
            f.write("Description=Robot HAT Web Server\n")
            f.write("After=network.target\n")
            f.write("\n")
            f.write("[Service]\n")
            f.write(
                "ExecStart=/bin/bash -c 'sleep 5 && sudo python3 "
                + thisPath
                + "/web/webServer_HAT_V3.1.py'\n"
            )
            f.write("User=pi\n")
            f.write("WorkingDirectory=" + thisPath + "\n")
            f.write("Restart=on-failure\n")
            f.write("\n")
            f.write("[Install]\n")
            f.write("WantedBy=multi-user.target\n")

        os.system("sudo systemctl daemon-reload")
        os.system("sudo systemctl enable robot_hat_startup.service")
        print("  Startup service configured successfully.")
    except Exception as e:
        print(f"  Error creating systemd service: {str(e)}")
        print("  Fallback to rc.local method...")


# Check if /etc/rc.local exists
print("\nConfiguring boot startup...")
if not os.path.exists("/etc/rc.local"):
    print("  /etc/rc.local does not exist.")
    if get_user_confirmation("  Create /etc/rc.local? "):
        os.system("sudo touch /etc/rc.local")
        os.system("sudo chown root:root /etc/rc.local")
        os.system("sudo chmod 755 /etc/rc.local")
        try:
            with open("/etc/rc.local", "w") as file_to_write:
                file_to_write.write(
                    "#!/bin/sh -e\n" + user_home + "/startup.sh start\nexit 0"
                )
            print("  /etc/rc.local created and configured.")
        except Exception as e:
            print(f"  Error: writing /etc/rc.local failed: {str(e)}")
    else:
        print("  Skipped creating /etc/rc.local.")
else:
    print("  /etc/rc.local exists. Configuring startup...")
    try:
        with open("/etc/rc.local") as f:
            content = f.read()
        if "robot_hat_startup" not in content:
            new_content = content + "\n" + user_home + "/startup.sh start\nexit 0"
            with open("/etc/rc.local", "w") as f:
                f.write(new_content)
            print("  Startup script added to /etc/rc.local.")
        else:
            print("  Startup script already configured in /etc/rc.local.")
    except Exception as e:
        print(f"  Error adding to /etc/rc.local: {str(e)}")


# Display a detailed summary of installation results
print("\n=== Installation Summary ===")
print("  APT Packages:")
if installation_results["apt"]["installed"]:
    print(f"    Installed: {', '.join(installation_results['apt']['installed'])}")
if installation_results["apt"]["failed"]:
    print(f"    Failed: {', '.join(installation_results['apt']['failed'])}")

print("  PIP Packages:")
if installation_results["pip"]["installed"]:
    print(f"    Installed: {', '.join(installation_results['pip']['installed'])}")
if installation_results["pip"]["failed"]:
    print(f"    Failed: {', '.join(installation_results['pip']['failed'])}")

print("  Other Components:")
if installation_results["other"]["installed"]:
    print(f"    Installed: {', '.join(installation_results['other']['installed'])}")
if installation_results["other"]["failed"]:
    print(f"    Failed: {', '.join(installation_results['other']['failed'])}")

# Prompt the user to confirm if they want to reboot
if get_user_confirmation("  Reboot the Raspberry Pi now? "):
    print("Rebooting...")
    os.system("sudo reboot")
else:
    print("Reboot cancelled. You may need to restart manually to complete the setup.")

# Final verification steps
print("\n=== Verification Summary ===")
print(
    "  1. I2C and start_x configuration: "
    + (
        "✅ Enabled"
        if "dtparam=i2c_arm=on" in open(check_config_file() or "").read()
        else "❌ Not enabled"
    )
)
print(
    "  2. Startup service: "
    + (
        "✅ Configured"
        if os.path.exists("/etc/systemd/system/robot_hat_startup.service")
        else "❌ Not configured"
    )
)
print(
    "  3. RC.local setup: "
    + ("✅ Configured" if os.path.exists("/etc/rc.local") else "❌ Not configured")
)

print("\nSetup complete. The Raspberry Pi is now ready for the Robot HAT installation.")
print(
    "Please power off the Raspberry Pi, connect the Robot HAT, and then power it on again."
)
print(
    "The web server will automatically start after the reboot. The setup script has been updated to handle package installation more robustly."
)
