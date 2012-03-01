BF3stats Plugin for Big Brother Bot
===================================
Display stats from [bf3stats.com](http://bf3stats.com) ingame.

Installation
------------
1. install the [bf3stats python module](https://github.com/ozon/python-bf3stats)
 - `easyinstall -U bf3stats`

2. install this plugin
 - copy the contents of `extplugins` to `b3/extplugins/`
 - add `<plugin name="bf3_stats" config="@b3/extplugins/conf/plugin_bf3stats.xml"/>` in your main b3 config file

Usage
-----
Use the command `!bf3stats` ingame to display your short stats.
You can use `!bf3stats <playername>` to display stats from other players.

Configuration
-------------
With [variables](https://github.com/ozon/b3-plugin-bf3stats/wiki/Variables) can you customize the output of the `!bf3stats` command.

The default configuration in plugin_bf3stats.xml:
`Stats for %(name)s: K/D: %(kd_ratio)s, Killstreak: %(killstreakbonus)s, Skill: %(elo)s`
This display: `Stats for O2ON: K/D: 1.61, Killstreak: 50, Skill: 592.02`

A list of available variables you can find in the [wiki](https://github.com/ozon/b3-plugin-bf3stats/wiki/Variables).

Thanks
------
- [bf3stats.com](http://bf3stats.com) for the nice API
