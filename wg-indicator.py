#!/usr/bin/python3

##############################################
#                                            #
#         ##########################         #
#         # Wireguard AppIndicator #         #
#         #      by decaby7e       #         #
#         #      2019-12-30        #         #
#         #        v1.0.0          #         #
#         ##########################         #
#                                            #
#  Features:                                 #
#   - Start and stop Wireguard VPN           #
#   - View status of VPN with use of icon    #
#   - View IP of interface                   #
#   - Quickly copy IP in menu by clicking    #
#                                            #
##############################################

# For menu and menu functions
import gi
import os
import sys
import time
import subprocess
import atexit

from os import path
from threading import Thread
from signal import signal, SIGINT
from sys import exit

# For getting IP address
import netifaces as ni

#GTK Related dependencies
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import GLib
from gi.repository import Notify as notify

APPINDICATOR_ID = 'wireguard_indicator'
BASE_DIR = os.path.expanduser('~/.config/wg-indicator')
CONFIG = BASE_DIR + '/config.json'
pid_file = BASE_DIR + '/wgindicator.pid'

# Create the base directory if it doesn't exist
if not os.path.exists(BASE_DIR):
    os.mkdir(BASE_DIR)

class Indicator():
    interface = 'wg0'
    
    def __init__(self):
        self.indicator = appindicator.Indicator.new(APPINDICATOR_ID, "network-offline", appindicator.IndicatorCategory.SYSTEM_SERVICES)
        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.build_menu())

        # Check status of Wireguard to change icon state
        # Daemonize the thread to make the indicator stopable
        self.update = Thread(target=self.monitor_vpn)
        self.update.setDaemon(True)
        self.update.start()

        notify.init(APPINDICATOR_ID)

    def build_menu(self):
        menu = gtk.Menu()

        start_vpn = gtk.MenuItem(label='Start VPN')
        start_vpn.connect('activate', self.up_vpn)

        stop_vpn = gtk.MenuItem(label='Stop VPN')
        stop_vpn.connect('activate', self.down_vpn)

        seperator= gtk.SeparatorMenuItem()

        self.vpn_ip = gtk.MenuItem(label='IP: Unknown')
        self.vpn_ip.connect('activate', self.copy_ip)

        menu.append(start_vpn)
        menu.append(stop_vpn)
        menu.append(seperator)
        menu.append(self.vpn_ip)

        menu.show_all()
        return menu

    def up_vpn(self, source):
        os.system("nohup sudo wg-quick up {0} >/dev/null 2>&1".format(self.interface))

    def down_vpn(self, source):
        os.system("nohup sudo wg-quick down {0} >/dev/null 2>&1".format(self.interface))

    def copy_ip(self, source):
        clipboard = gtk.Clipboard.get(gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(self.get_ip(), -1)

    def get_ip(self):
        try:
            ni.ifaddresses(self.interface)
            return ni.ifaddresses(self.interface)[ni.AF_INET][0]['addr']
        except:
            return 'Unknown'

    def monitor_vpn(self):
        while True:
            time.sleep(1)

            if len(subprocess.check_output(['sudo', 'wg', 'show', self.interface])) == 0:
                GLib.idle_add(
                        self.indicator.set_icon,
                        "network-offline",
                        priority=GLib.PRIORITY_DEFAULT
                )
                self.vpn_ip.set_label('IP: ' + self.get_ip())
            else:
                GLib.idle_add(
                        self.indicator.set_icon,
                        "network-vpn",
                        priority=GLib.PRIORITY_DEFAULT
                )
                self.vpn_ip.set_label('IP: ' + self.get_ip())

# Basic service management: Only allows once instance of this to run at a time
def daemonize(action):
    global pid_file

    if action == 'up':
        try:
            open(pid_file, 'r')
            print('[ Error ] Service already running. Check ~/.config/wg-indicator for dead PID files?')
            hard_exit()

        except IOError:
            open_pid = open(pid_file, 'w')
            open_pid.write( str(os.getpid()) )
            open_pid.close()

    elif action == 'down':
        try:
            open_pid = open(pid_file, 'r')
            pid = open_pid.readline()
            os.kill(int(pid), 15)
            open_pid.close()
            sys.exit()

        except IOError:
            print('[ Error ] Service not running. Check ~/.config/wg-indicator for dead PID files?')
            hard_exit()

    else:
        raise ValueError


def exit_handler():
    print('[ Info ] Exit signal detected. Exiting gracefully...')

    try:
        os.remove(pid_file)
    except IOError:
        print('[ Error ] PID file not found. Is the indicator running?')

def hard_exit():
    atexit.unregister(exit_handler)
    sys.exit()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('[ Error ] Missing argument. Specify \'up\' or \'down\'')
        sys.exit()

    atexit.register(exit_handler)

    daemonize(sys.argv[1])
    
    Indicator()
    gtk.main()
