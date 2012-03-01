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

import base64
import hashlib
import hmac

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

    def _add_kd(self, stats):
        """Calc and update stats with K/D and W/L ratio"""
        stats['global']['kd_ratio'] = stats['global']['kills'] / float(stats['global']['deaths'])
        stats['global']['wl_ratio'] = stats['global']['wins'] / float(stats['global']['losses'])
        return stats

    def get_pretty_short_stats(self, player_name):
        """Return short stats"""
        # request stats and status
        stats, status = self.stats_api.get_player_stats(player_name, 'clear,global')
        if status == 'data':
            stats = self._add_kd(stats)
            stats = stats['global']
            output = 'Stats for %s: K/D: %.2f, Killstreak: %d, Skill: %d' % (player_name, stats['kd_ratio'], stats['killstreakbonus'], stats['elo'] )
        elif status == 'notfound':
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


class Bf3StatsAPI(object):
    def __init__(self, plugin):
        self.player_stats = None
        self._plugin = plugin
        self.api_url = None
        self.secretKEY = self._plugin.config.get('secrets', 'key')
        self.ident = self._plugin.config.get('secrets', 'ident')
        self._playerupdate_results = None
        self._player_name = None

    def _request(self, post_data, data_group):
        """Request data from bf3stats.com"""
        url='http://api.bf3stats.com'
        plattform='pc'
        api_url = '%s/%s/%s/' % (url, plattform, data_group)
        try:
            con = urllib.urlopen(api_url, urllib.urlencode(post_data))
            result = con.read()
            con.close()
            rawdata = json.loads(result)
        except IOError:
            self._plugin.debug('IOError - we have some Network trouble!')
            rawdata = {'status' : 'fetch_fail'}
        return rawdata

    def _signed_request(self, data_dict, data_group):
        """Request data from bf3stats.com with a signed request"""
        data = self._base64_url_encode(json.dumps(data_dict))
        sig = self._base64_url_encode(hmac.new(self.secretKEY, msg=data, digestmod=hashlib.sha256).digest())
        post_data = { 'data': data, 'sig': sig}
        return self._request(post_data, data_group)



    def get_player_stats(self, player_name, parts=None):
        self._player_name = player_name
        post_data = {'player' : self._player_name, 'opt' : parts }
        self._plugin.debug('Get Stats for %s , opts: %s ' % ( self._player_name, parts))
        self.rawdata = self._request(post_data, data_group='player')
        # @todo cache data
        self.verify_data()
        return self.player_stats, self.rawdata['status']

    def _request_playerupdate(self):
        """Request playerupdate"""
        post_data = { 'ident': self.ident, 'time': int(time.time()), 'player': self._player_name }
        self._playerupdate_results = self._signed_request(post_data, data_group='playerupdate')

    def do_playerupdate(self):
        # request playerupdate
        self._plugin.debug('Request playerupdate for %s', self._player_name)
        self._request_playerupdate()
        # @todo: handle status.timeout
        retry = 1
        while self._playerupdate_results['task']['state'] == 'queued':
            time.sleep(15)
            self._request_playerupdate()
            retry = retry + 1
            if retry == 5:
                self._plugin.debug('Request playerupdate for %s failed!', self._player_name)
                status = 'error'
                break
        if self._playerupdate_results['task']['state'] == 'finished':
            status = self._playerupdate_results['task']['result']
        self._plugin.debug('Request playerupdate done. Status: %s', status)
        return status

    def _base64_url_encode(self, data):
        return base64.urlsafe_b64encode(data).rstrip('=')

    # handle status
    def verify_data(self):
        handle_status = {
                'notfound': self._handle_status_notfound,
                'data': self._handle_status_data,
                'pifound': self._handle_status_pifound,
                'error': self._handle_status_error,
                }
        status = self.rawdata['status']
        handle_status[status]()

    def _handle_status_data(self):
        sec = 86400 # 1 day
        last_update =  self.rawdata['stats']['date_update']
        self._plugin.debug('%s ´s stats last updated: %s', self._player_name, time.ctime(last_update))
        self.player_stats = self.rawdata['stats']

    def _handle_status_notfound(self):
        self._plugin.debug('Player not found!')
        self.do_playerupdate()

    def _handle_status_pifound(self):
        self._plugin.debug('%s found in the player index, but no data currently available.', self._player_name)
        self.do_playerupdate()
        self.get_player_stats(self._player_name)

    def _handle_status_error(self):
        err = self.rawdata['error']
        self._plugin.debug('Error: %s', err)


if __name__ == '__main__':
    from b3.fake import fakeConsole, superadmin

    myplugin = Bf3StatsPlugin(fakeConsole, '@b3/extplugins/conf/plugin_bf3stats.xml')
    myplugin.onStartup()
    time.sleep(3)
    superadmin.connects(cid=0)
    api = Bf3StatsAPI(myplugin)

    def _test_get_player_stats(player='O2ON'):
        print api.get_player_stats(player)

    def _test_player_update(player='O2ON'):
        print api.playerupdate(player)

    #superadmin.says('!bfstats')

