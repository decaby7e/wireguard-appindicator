#!/usr/bin/python

import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk, AppIndicator3 as appindicator


def main():
    indicator = appindicator.Indicator.new("customtray", "network-vpn", appindicator.IndicatorCategory.APPLICATION_STATUS)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(menu())
    gtk.main()
def menu():
    menu = gtk.Menu()
    
    command_one = gtk.MenuItem('Start Wireguard')
    command_one.connect('activate', start_wireguard)
    menu.append(command_one)

    command_two = gtk.MenuItem('Stop Wireguard')
    command_two.connect('activate', stop_wireguard)
    menu.append(command_two)

    exittray = gtk.MenuItem('Exit')
    exittray.connect('activate', quit)
    menu.append(exittray)
    
    menu.show_all()
    return menu


def start_wireguard(_):
    os.system("wg-quick up wg0")
def stop_wireguard(_):
    os.system("wg-quick down wg0")
def quit(_):
    gtk.main_quit()


if __name__ == "__main__":
    main()