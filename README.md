# PiPyMaintenance
Python script for systemctl services, WiFi and bluetooth maintenance for Raspberry Pi Raspbian systems

The script checks in a user define interval the status of defined services, WiFi wlan0 and bluetooth and modifies them as defined in the config file, it also has a special implementation for ufw and Pi-Hole.

It generates a output.log with information of changes and errors

### Dependencies:
manual install `pyyaml`
```
$ pip install pyyaml
```
or using [requirements.txt](requirements.txt)
```
$ pip install -r requirements.txt
```
### Configuration

The [config.yaml](config.yaml) file  is divided in three sections:
- Services, list of services to be checked, True or False indicate if checked and enabled or not checked (only enable services if True, can't disable)
- WiFi and bluetooth, True or False for enabling or disabling.
- Interval, sets the time interval for the loop to repeat.

More services can be added without modifying the script if "systemctl status" compatible, add the full name without the ".service" to the [config.yaml](config.yaml) service list.

### Getting Started

Tested in Raspbian 9 (stretch) & Python3.7

Steps:

```
$ sudo cp maintenance.service /etc/systemd/system/maintenance.service

$ sudo chmod 644 /etc/systemd/system/maintenance.service

$ chmod +x /home/pi/PiPymaintenance/maintenance.py

$ sudo systemctl daemon-reload

$ sudo systemctl enable maintenance.service

$ sudo systemctl start maintenance.service
```
