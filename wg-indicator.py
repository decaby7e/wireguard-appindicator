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

class Indicator():
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
        os.system("nohup sudo wg-quick up wg0 >/dev/null 2>&1")

    def down_vpn(self, source):
        os.system("nohup sudo wg-quick down wg0 >/dev/null 2>&1")

    def copy_ip(self, source):
        clipboard = gtk.Clipboard.get(gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(self.get_ip(), -1)

    def get_ip(self):
        try:
            ni.ifaddresses('wg0')
            return ni.ifaddresses('wg0')[ni.AF_INET][0]['addr']
        except:
            return 'Unknown'

    def monitor_vpn(self):
        while True:
            time.sleep(1)

            if len(subprocess.check_output(['sudo', 'wg'])) == 0:
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
def service():
	if len(sys.argv) < 2:
		print('ERROR: Missing argument. Specify \'up\' or \'down\'')
		sys.exit()

	if sys.argv[1] == 'up':
		if path.exists('app.run'):
			print('ERROR: Service already running. (Remove app.run if this is a mistake)')

			sys.exit()
		else:
			pid_file = open('app.run', 'w')
			pid_file.write( str(os.getpid()) )
			pid_file.close()

	elif sys.argv[1] == 'down':
		pid_file = open('app.run', 'r')
		pid = pid_file.readline()
		os.system( "kill {0}".format(pid) )
		pid_file.close()

		os.system("rm app.run")

		sys.exit()
	
	else:
		print('ERROR: Invalid argument. Specify \'up\' or \'down\'')

		sys.exit()

def sigint_handler(signal_received, frame):
	print('SIGINT detected. Exiting gracefully')
	os.system("rm app.run")
	sys.exit()

def exit_handler():
	print('Exit signal detected. Exiting gracefully')
	os.system("rm app.run")
	sys.exit()

if __name__ == '__main__':
	signal(SIGINT, sigint_handler)
	atexit.register(exit_handler)
	
	service()
	
	Indicator()
	gtk.main()
