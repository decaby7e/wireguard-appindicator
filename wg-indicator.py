#!/usr/bin/python3

import gi
import os
import signal
import time
import subprocess
from threading import Thread

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from gi.repository import Gtk as gtk
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

        item_quit = gtk.MenuItem(label='Quit')
        item_quit.connect('activate', self.quit)

        menu.append(start_vpn)
        menu.append(stop_vpn)
        menu.append(item_quit)
        menu.show_all()
        return menu

    def up_vpn(self, source):
        os.system("wg-quick up wg0")

    def down_vpn(self, source):
        os.system("wg-quick down wg0")

    def monitor_vpn(self):
        while True:
            time.sleep(1)
            
            if len(subprocess.check_output(['sudo', 'wg'])) == 0:
                GLib.idle_add(
                        self.indicator.set_icon,
                        "network-offline",
                        priority=GLib.PRIORITY_DEFAULT
                )
            else:
                GLib.idle_add(
                        self.indicator.set_icon,
                        "network-vpn",
                        priority=GLib.PRIORITY_DEFAULT
                )
            
    def quit(self, source):
        gtk.main_quit()


Indicator()
signal.signal(signal.SIGINT, signal.SIG_DFL)
gtk.main()