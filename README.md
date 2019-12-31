# Wireguard AppIndicator
## Configuration
As of 2019.12.24, you must manually configure your interface name if it is not wg0 by modifying the script. In the future, I will make this a cleaner process.

## Usage
To use this indicator app, either install the provided Gnome Shell extension or run the standalone script.

IMPORTANT: You must add an exception in the /etc/sudoers file for the wg and wg-quick commands. Tutorials of how to do this for any command can be found anywhere on Google.