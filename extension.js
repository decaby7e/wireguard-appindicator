/* extension.js
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * SPDX-License-Identifier: GPL-2.0-or-later
 */

/* exported init */

class Extension {
   constructor(){}

    enable() {
	const Util = imports.misc.util;
        let python_script = '/home/decaby7e/.local/share/gnome-shell/extensions/wireguard-appindicator@decaby7e.ranvier.net/wg-indicator.py';
        Util.spawnCommandLine(python_script + " up");
    }

    disable() {
	const Util = imports.misc.util;
        let python_script = '/home/decaby7e/.local/share/gnome-shell/extensions/wireguard-appindicator@decaby7e.ranvier.net/wg-indicator.py';
        Util.spawnCommandLine(python_script + " down");
    }
}

function init() {
    return new Extension();
}
