# General Notes

## 2025-12-13

1. Noted an update to the requirements.txt file which added types for flask-cors. This seemed to resolve the compatibility issues for package handling even with attempting to run the basic scripts from a "normal" raspberry pi user within a venv. Looks like we can work this into the code workflow to isolate the processes associated with this repo if needed.

2. Do this when creating the venv to setup the libcamera package for picamera2
   - ```bash
       sudo apt install -y python3-libcamera
       python3 -m venv --system-site-packages .venv
     ```

3. For the imx219 configuration changes were required to `/boot/firmware/config.txt` (current generation pi OS) as noted in [Arducam Wiki for IMX219](https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/8MP-IMX219/) as:

   a. Open the configuration file:
   - `sudo nano /boot/firmware/config.txt`

   b. Disable camera auto-detection:
   - `camera_auto_detect=0`

   - Changes these lines from:

   - ```text
       line 18: # Automatically load overlays for detected cameras
       line 19: camera_auto_detect=1
     ```

   - Updated to:

   - ```text
       line 18: # Automatically load overlays for detected cameras
       line 19: camera_auto_detect=0
     ```

   c. Add imx219 overlay under the [all] section:
   - `dtoverlay=imx219`

   - Changes these lines from:

   - ```text
       line 53: [all]
       line 54:
     ```

   - Updated to:

   - ```text
       line 53: [all]
       line 54: dtoverlay=imx219
       line 55:
     ```

   d. Save and reboot:
   - `sudo reboot`

Recommend: Add detection and handling for different camera models to be included from the start.

## 2025-12-1

```bash
 python ./web/webServer_HAT_V3.1.py
[0:28:06.568720599] [3422]  INFO Camera camera_manager.cpp:340 libcamera v0.6.0+rpt20251202
[0:28:06.577285510] [3425]  INFO RPI pisp.cpp:720 libpisp version 1.3.0
[0:28:06.579718760] [3425]  INFO IPAProxy ipa_proxy.cpp:180 Using tuning file /usr/share/libcamera/ipa/rpi/pisp/imx219.json
[0:28:06.586910509] [3425]  INFO Camera camera_manager.cpp:223 Adding camera '/base/axi/pcie@1000120000/rp1/i2c@80000/imx219@10' for pipeline handler rpi/pisp
[0:28:06.586933861] [3425]  INFO RPI pisp.cpp:1181 Registered camera /base/axi/pcie@1000120000/rp1/i2c@80000/imx219@10 to CFE device /dev/media0 and ISP device /dev/media1 using PiSP variant BCM2712_D0
[0:28:06.589818553] [3422]  INFO Camera camera.cpp:1215 configuring streams: (0) 640x480-XBGR8888/SMPTE170M/Rec709/None/Full (1) 640x480-BGGR_PISP_COMP1/RAW
[0:28:06.589929757] [3425]  INFO RPI pisp.cpp:1485 Sensor: /base/axi/pcie@1000120000/rp1/i2c@80000/imx219@10 - Selected sensor format: 640x480-SBGGR10_1X10/RAW - Selected CFE format: 640x480-PC1B/RAW
/usr/lib/python3/dist-packages/gpiozero/input_devices.py:852: PWMSoftwareFallback: For more accurate readings, use the pigpio pin factory.See https://gpiozero.readthedocs.io/en/stable/api_input.html#distancesensor-hc-sr04 for more info
  warnings.warn(PWMSoftwareFallback(
......................pause..........................
Please check the configuration in /boot/firmware/config.txt.
You can turn on the 'SPI' in 'Interface Options' by using 'sudo raspi-config'.
Or make sure that 'dtparam=spi=on' is not commented, then reboot the Raspberry Pi. Otherwise spi0 will not be available.
no running event loop
...
no running event loop
 * Serving Flask app 'app'
no running event loop
no running event loop
no running event loop
 * Debug mode: off
no running event loop
...
no running event loop
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.1.186:5000
no running event loop
no running event loop
Press CTRL+C to quit
no running event loop
...
no running event loop
...
# ended script
```

Noted:

```bash
......................pause..........................
Please check the configuration in /boot/firmware/config.txt.
You can turn on the 'SPI' in 'Interface Options' by using 'sudo raspi-config'.
Or make sure that 'dtparam=spi=on' is not commented, then reboot the Raspberry Pi. Otherwise spi0 will not be available.
```

Updated boot config to include `dtparam=spi=on` which was commented out.

---
