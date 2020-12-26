#!/usr/bin/python

#Raspbian maintenance script by @moradorex

import time
import subprocess
import yaml
import logging


def nextword(target, source):
   for i, w in enumerate(source):
     if w == target:
       return source[i+1]

def check_service(service):
    try:
        output = subprocess.run(["sudo", "systemctl", "status", service+".service"], capture_output=True, shell=False)
        if(nextword('Active:', str(output).split()) == 'active'):
            return True
        else:
            return False
    except:
        return False

def start_service(service):
    try:
        output = subprocess.run(["sudo", "systemctl", "start", service+".service"], capture_output=True, shell=False)
        if(output.stderr != b''):
            return False
        return True
    except:
        return False

def check_pihole():
    try:
        output = subprocess.run(["sudo", "pihole", "status"], capture_output=True, shell=False)
        if(output.stdout != b'  [\xe2\x9c\x93] DNS service is listening\n     [\xe2\x9c\x93] UDP (IPv4)\n     [\xe2\x9c\x93] TCP (IPv4)\n     [\xe2\x9c\x93] UDP (IPv6)\n     [\xe2\x9c\x93] TCP (IPv6)\n\n  [\xe2\x9c\x93] Pi-hole blocking is enabled\n'):
            return False
        return True
    except:
        return False

def enable_pihole():
    try:
        output = subprocess.run(["sudo", "pihole", "enable"], capture_output=True, shell=False)
        if(output.stdout == b'  [i] Enabling blocking\n\r\x1b[K  [\xe2\x9c\x93] Pi-hole Enabled\n' or output.stdout == b'  [i] Blocking already enabled, nothing to do\n'):
            return True
        return True
    except:
        return False

def check_ufw():
    try:
        output = subprocess.run(["sudo", "ufw", "status"], capture_output=True, shell=False)
        splited_output = str(output).split()
        active = nextword('stdout=b\'Status:', splited_output)
        if(active == 'active\\n\\nTo'):
            return True
        return False
    except:
        return False

def enable_ufw():
    try:
        process = subprocess.Popen(["sudo", "ufw", "enable"],
                               shell=False,
                               bufsize=0,
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        process.stdin.write(b'y\n')
        output = process.stdout.read()
        process.terminate()
        if(output != b'Command may disrupt existing ssh connections. Proceed with operation (y|n)? Firewall is active and enabled on system startup\n' ):
            return True
        return False
    except:
        return False

def check_WiFi(interface):
    try:
        output = subprocess.run(["sudo", "ifconfig"], capture_output=True, shell=False)
        if interface in output.stdout.decode("utf-8"):
            return True
        else: 
            return False
    except:
        return False

def change_WiFi(interface, mode):
    try:
        output = subprocess.run(["sudo", "ifconfig", interface, mode], capture_output=True, shell=False)
        if(output.stderr != b''):
            return False
        return True
    except:
        return False

def change_bluetooth(mode):
    if(mode):
        smode = 'restart'
    else:
        smode = 'stop'

    try:
        output = subprocess.run(["sudo", "invoke-rc.d", "bluetooth", smode], capture_output=True, shell=False)
        if(output.stderr != b''):
            return False
        return True
    except:
        return False

def log_services(is_enabled, service):
    try:
        with open("output.log", "a") as log_file:
            if(is_enabled):
                log_file.write(str(time.strftime('%Y-%m-%d %H:%M:%S')) + " - Service: " + str(service) + " was not enabled and is now enabled\n")
            else:
                log_file.write(str(time.strftime('%Y-%m-%d %H:%M:%S')) + " - Service: " + str(service) + ", error enabling service - service is down\n")
            log_file.close()
    except:
        logging.info("log_services Error")

def log_wifi(changed, interface, WiFi):
    try:
        with open("output.log", "a") as log_file:
            if(changed):
                log_file.write(str(time.strftime('%Y-%m-%d %H:%M:%S')) + " - WiFi, Interface: " + str(interface) + " is now " + str(WiFi) + "\n")
            else:
                log_file.write(str(time.strftime('%Y-%m-%d %H:%M:%S')) + " - WiFi, Interface: " + str(interface) + " error, couldn't be changed to " + str(WiFi) + "\n")
            log_file.close()
    except:
        logging.info("log_wifi Error")

def log_bluetooth(changed, bluetooth):
    try:
        with open("output.log", "a") as log_file:
            if(changed):
                log_file.write(str(time.strftime('%Y-%m-%d %H:%M:%S')) + " - bluetooth is now " + str(bluetooth) + "\n")
            else:
                log_file.write(str(time.strftime('%Y-%m-%d %H:%M:%S')) + " - bluetooth error couldn't be changed to " + str(bluetooth) + "\n")
            log_file.close()
    except:
        logging.info("log_bluetooth Error")


def main():
    time.sleep(10)

    while True:

        #Config File
        try:
            with open("config.yaml", "r") as yamlfile:
                data = yaml.load(yamlfile, Loader=yaml.FullLoader)
                service_dict = data['services']
                interval = int(data['interval'])
                WiFi = data['WiFi']
                bluetooth = data['bluetooth']
                yamlfile.close()
        except:
            logging.info("Config File Reading Error")

        #Dict to list and discard False
        service_list = []
        for service in service_dict.keys():
            if(service_dict[service]):
                service_list.append(service)

        #Check and enable services
        for service in service_list:

            #Variables
            was_enabled = True
            is_enabled = True

            #ufw
            if(service == 'ufw'):
                was_enabled = check_ufw()
                if not(was_enabled):
                    is_enabled = enable_ufw()

                    #log
                    log_services(is_enabled, service)

            #pihole-FTL
            elif(service == 'pihole-FTL'):
                was_enabled = check_service(service)
                if(was_enabled):
                    was_enabled = check_pihole()
                    if not(was_enabled):
                        is_enabled = enable_pihole()
                else:
                    is_enabled = start_service(service)
                    time.sleep(5)
                    is_enabled = enable_pihole()

                #log
                if not(was_enabled):
                    log_services(is_enabled, service)

            #other services with only systemd status
            else:
                was_enabled = check_service(service)
                if not(was_enabled):
                    is_enabled = start_service(service)

                    #log
                    log_services(is_enabled, service)

        #WiFi
        changed = False
        if(WiFi != check_WiFi('wlan0')):
            if(WiFi):
                changed = change_WiFi('wlan0', 'up')
            else:
                changed = change_WiFi('wlan0', 'down')

            log_wifi(changed, 'wlan0', WiFi)

        #bluetooth
        changed = False
        if(bluetooth != check_service(bluetooth)):
            if(WiFi):
                changed = change_bluetooth(bluetooth)
            else:
                changed = change_bluetooth(bluetooth)

            log_bluetooth(changed, bluetooth)

        time.sleep(interval)


if __name__ == "__main__":
    main()

