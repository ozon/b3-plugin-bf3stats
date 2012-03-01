#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Harry Gabriel <h.gabriel@nodefab.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Changelog:
#


import b3
import b3.plugin
import time
#from datetime import datetime

import bf3stats



__version__ = '0.1'
__author= 'ozon'

class Bf3_StatsPlugin(b3.plugin.Plugin):
    _adminPlugin = None
    playerstats = None
    _bf3stats = None
    _bf3stats_ident = None
    _bf3stats_secret = None

    def onLoadConfig(self):
        # get bf3stats API key from config
        try:
            self._bf3stats_ident = self.config.get('secrets', 'ident')
        except ValueError, err:
            self.debug(err)
            self.warning('No bf3stats API ident found.')
        try:
            self._bf3stats_secret = self.config.get('secrets', 'key')
        except ValueError, err:
            self.debug(err)
            self.warning('No bf3stats API key found.')

    def onStartup(self):
        """Initialize plugin settings """
        # try to load admin plugin
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            self.error('Could not find admin plugin')
            return False
        # register our command
        self._registerCommands()
        # get bf3stats API
        self._bf3stats = bf3stats.api(ident=self._bf3stats_ident, secret=self._bf3stats_secret)

    def cmd_bf3stats(self, data, client, cmd=None):
        """\
        [player] - show short stats from bf3stats.com
        """
        short_stats = ''
        if not data:
            short_stats = self.get_pretty_short_stats(client.name)
        else:
            args = cmd.parseData(data)
            sclient = self._adminPlugin.findClientPrompt(args[0], client)
            if not sclient:
                # no matching player found - exit here
                return
            else:
                short_stats = self.get_pretty_short_stats(sclient.name)

        self.console.say(short_stats)

    ### some helper functions to handle stats data

    def _calc_ratio(self, win, loss):
        """Calc and return ratio"""
        return win / float(loss)

    def get_pretty_short_stats(self, player_name):
        """Return short stats"""
        # request stats and status
        player_stats = self._bf3stats.player(player_name, 'clear,global')
        if player_stats.status == 'data':
            kd_ratio = self._calc_ratio(player_stats.Stats.Global.kills, player_stats.Stats.Global.deaths)
            #wl_ratio = self._calc_ratio(player_stats.Stats.Global.wins, player_stats.Stats.Global.losses)
            output = 'Stats for %s: K/D: %.2f, Killstreak: %d, Skill: %d' % (player_name, kd_ratio, player_stats.Stats.Global.killstreakbonus, player_stats.Stats.Global.elo )
        elif player_stats.status == 'notfound':
            output = 'Player not found'

        return output

    ### Other missing functions that should be included in B3 ;)
    def _getCmd(self, cmd):
        cmd = 'cmd_%s' % cmd
        if hasattr(self, cmd):
            func = getattr(self, cmd)
            return func
        return None

    def _registerCommands(self):
        """Map/Register all commands they found in 'commands' configuration section """
        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp
                func = self._getCmd(cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)


if __name__ == '__main__':
    from b3.fake import fakeConsole, superadmin


    myplugin = Bf3_StatsPlugin(fakeConsole, '@b3/extplugins/conf/plugin_bf3stats.xml')
    myplugin.onStartup()
    time.sleep(3)
    superadmin.connects(cid=0)


    #superadmin.says('!bfstats')

