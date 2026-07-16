# View and record Dental Camera video stream frames as a sequence of JPEG images

<figure align="center">
  <img src="image/screenshot.jpg" alt="Screenshot of GUI" width="640px"/>
  <figcaption>Screenshot of GUI</figcaption>
</figure>

<figure align="center">
  <img src="image/dental_camera.jpg" alt="Dental Camera" width="640px"/>
  <figcaption>Dental Camera</figcaption>
</figure>

<figure align="center">
  <img src="image/example.webp" alt="Example sequence of recorded frame images" width="640px"/>
  <figcaption>Example sequence of recorded frame images</figcaption>
</figure>

Author: [Mark Hsieh](https://github.com/mcmhsieh)

## Acknowledgements
 * Substantially based on [MJPEG Mirror for Suear "Smart" Ear Cleaners](https://github.com/SeanPesce/Suear-Web-Viewer) by [Sean Pesce](https://github.com/SeanPesce)

## Purpose

The recorded frame are saved to a directory as individual JPEG images files, which makes them readily viewable and selectable as input for my research project, currently under development, to generate systhesised views by stitching together the collection of frame images.

<figure align="center">
  <img src="image/synthesised_view.jpg" alt="Example synthesised view generated from a longer sequence of frames" width="640px"/>
  <figcaption>Example synthesised view generated from a longer sequence of frames</figcaption>
</figure>

## About the dental camera

Bought from an online marketplace with very little information about its manufacturer or model on the item's listing, packaging, instructions or the device itself.

The instructions call it "Model: 401", and directs the user to use an app called "ANESOK" on Google Play or Apple App store.

Its Wifi SSID is "ANESOK-401-*xxxx*", and the vendor/model/version information it returns once connected is "YPC/TX806-XRH-401/V24".

Searching online, it appears to be the [SUNUO® 401 Wifi Dental Camera Oral Endoscope](http://anesoksunuo.com/dental-camera/199.html) made by Shenzhen Sulang Technology Co., Ltd, "ANESOK" and "INSKAM" seem to be alternative names associated with "SUNUO".

<figure align="center">
  <img src="image/dental_camera.jpg" alt="Dental Camera" width="640px"/>
  <figcaption>Dental Camera</figcaption>
</figure>

There is further information about the family devices in the [README of Sean Pesce's MJPEG Mirror for Suear "Smart" Ear Cleaners](https://github.com/SeanPesce/Suear-Web-Viewer/blob/main/README.md).

## Usage (Microsoft Window)

- Clone or download repo
- Install Python 3.11 and Python Poetry
- Create a virtual environment and use Poetry to install the dependencies
- Remove the stick-on clear plastic film covering the LEDs and camera lens on the Dental Camera device. This will improve the clarity of the captured images.
- Power on the Dental Camera device and set the LED brightness to the dimmest setting
- Connect to the Dental Camera device's WiFi ("ANESOK-401-*xxxx*")
  - Optionally set the WiFi connection as a private connection
  - Optionally manually add a Windows Firewall inbound rule for python.exe (or add it at the automatic prompt when the frame recorder utility is run for the first time)
  - Optionally add an IPv4 route for 192.168.1.1 to the WiFi interface (in an elevated command prompt) if the system is connected to another router (e.g. via Ethernet) that is also at 192.168.1.1
- Run the frame recorder utility `python.exe frame_recorder.py`
- Click the "Start recording" button (or hit space bar key) to start and stop recording images to the `./recorded_frames` subdirectory

## License

[GNU General Public License v2.0](LICENSE)
