#!/usr/bin/python
import os
from gi.repository import Gtk as gtk, AppIndicator3 as appindicator
def main():
    indicator = appindicator.Indicator.new("customtray", "semi-starred-symbolic", appindicator.IndicatorCategory.APPLICATION_STATUS)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(menu())
    gtk.main()
def menu():
    menu = gtk.Menu()
    
    command_one = gtk.MenuItem('My Notes')
    command_one.connect('activate', note)
    menu.append(command_one)
    exittray = gtk.MenuItem('Exit Tray')
    exittray.connect('activate', quit)
    menu.append(exittray)
    
    menu.show_all()
    return menu
    
def note(_):
    os.system("gedit $HOME/Documents/notes.txt")
def quit(_):
    gtk.main_quit()
if __name__ == "__main__":
    main()