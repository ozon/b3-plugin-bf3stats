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
import json # @todo: fallback for older/other python/json versions
import urllib
import time
#from datetime import datetime

__version__ = '0.1'
__author= 'ozon'

class Bf3StatsPlugin(b3.plugin.Plugin):
    _adminPlugin = None
    playerstats = None

    def onLoadConfig(self):
        self.stats_api = Bf3StatsAPI(self)

    def onStartup(self):
        """Initialize plugin settings """
        # try to load admin plugin
        self._adminPlugin = self.console.getPlugin('admin')
        if not self._adminPlugin:
            self.error('Could not find admin plugin')
            return False
        # register our command
        self._registerCommands()

    def cmd_bf3stats(self, data, client, cmd=None):
        """Handle !bf3stats command """
        # post own stats
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

    def get_global_stats(self, player_name):
        stats, status = self.stats_api.fetch_stats(player_name, 'clear,global')
        stats['global']['kd_ratio'] = stats['global']['kills'] / float(stats['global']['deaths'])
        stats['global']['wl_ratio'] = stats['global']['wins'] / float(stats['global']['losses'])

        return stats['global']

    def get_pretty_short_stats(self, player_name):
        """Return short status """
        stats = self.get_global_stats(player_name)
        return 'Stats for %s: K/D: %.2f, Killstreak: %d, Skill: %d' % (player_name, stats['kd_ratio'], stats['killstreakbonus'], stats['elo'] )

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


class Bf3StatsAPI(object):
    def __init__(self, plugin):
        url='http://api.bf3stats.com'
        plattform='pc'
        data_group='player'
        # setup api_url
        self.api_url = '%s/%s/%s/' % (url, plattform, data_group)
        self._statsdata = {}
        self._plugin = plugin

    def fetch_stats(self, player_name, parts=None):
        post_data = {'player' : player_name, 'opt' : parts }
        # fetch our data from web
        try:
            self._plugin.debug('Get Stats for %s from %s, opts: %s ' % ( player_name, self.api_url, parts))
            con = urllib.urlopen(self.api_url, urllib.urlencode(post_data))
            result = con.read()
            con.close()
            rawdata = json.loads(result)
        except IOError:
            self._plugin.debug('IOError - we have some Network trouble!')
            rawdata = {'status' : 'fetch_fail'}

        # @todo verify status
        # @todo cache data
        stats = {}
        if rawdata['status'] == 'data':
            # @todo: check date and request refresh if to old
            stats = rawdata['stats']
        elif rawdata['status'] == 'notfound':
            # @todo: request update/find player and try again
            self._plugin.debug('Player not found.')
        elif rawdata['status'] == 'error':
            err = rawdata['error']
            self._plugin.debug('Error: %s', err)

        return stats, rawdata['status']



#    def _verify_status(self):
#        # check if data a dict and has status key
#        if type(data).__name__ == 'dict' and 'status' in data:
#            if data['status'] == 'data':
#                return True
#            elif data['status'] == 'notfound':
#                # @todo request update and try again
#                self._plugin.debug('Status: Player not found')
#                return False
#            elif data['status'] == 'error':
#                self._plugin.debug('Error: %s, reasons: %s' % ( data['error'], data['reasons'] ))
#                return False
#            else:
#                self._plugin.debug('Unknown status %s - Please send output to developer' % data['status'])
#                return False


if __name__ == '__main__':
    from b3.fake import fakeConsole, superadmin

    myplugin = Bf3StatsPlugin(fakeConsole, '@b3/extplugins/conf/plugin_bf3stats.xml')
    myplugin.onStartup()
    time.sleep(3)
    superadmin.connects(cid=0)
    api = Bf3StatsAPI(myplugin)

    superadmin.says('!bfstats')
    #print api.fetch_from_api(myplugin.data)

