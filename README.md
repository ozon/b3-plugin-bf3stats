BF3stats Plugin for Big Brother Bot
===================================
Display stats from [bf3stats.com](http://bf3stats.com) ingame.

Installation
------------
1. install the [bf3stats python module](https://github.com/ozon/python-bf3stats)
 - `easyinstall -U bf3stats` or down the [bf3stats module](https://github.com/ozon/python-bf3stats/zipball/master) and copy the folder `bf3stats` in your b3 plugin folder

2. install this plugin
 - copy the contents of `extplugins` to `b3/extplugins/`
 - add `<plugin name="bf3stats" config="@b3/extplugins/conf/plugin_bf3stats.xml"/>` in your main b3 config file

Usage
-----
Use the command `!bf3stats` ingame to display your short stats.
You can use `!bf3stats <playername>` to display stats from other players.

Configuration
-------------
With variables can you customize the output of the `!bf3stats` command.

The default configuration in plugin_bf3stats.xml:
`Stats for %(name)s: K/D: %(kd_ratio)s, Killstreak: %(killstreakbonus)s, Skill: %(elo)s`
This display: `Stats for O2ON: K/D: 1.61, Killstreak: 50, Skill: 592.02`

The following variables can be set:

| __Variable__            | __Description__ |
| ----------------------- | :-------------- |
| (avengerkills)s         | |
| (damagaassists)s        | |
| (deaths)s               | |
| (dogtags)s              | |
| (elo)s                  | Skill |
| (elo_games)s            | |
| (flagcaps)s             | |
| (flagdef)s              | |
| (headshots)s            | |
| (heals)s                | |
| (hits)s                 | |
| (kd_ratio)s             | |
| (killassists)s          | |
| (kills)s                | Kills |
| (killstreakbonus)s      | Killstreak |
| (last_update)s          | |
| (longesthandhs)s        | |
| (longesths)s            | |
| (losses)s               | |
| (mcomdefkills)s         | |
| (mcomdest)s             | |
| (name)s                 | Playername |
| (nemesiskills)s         | |
| (nemesisstreak)s        | |
| (repairs)s              | |
| (resupplies)s           | |
| (revives)s              | |
| (rounds)s               | |
| (saviorkills)s          | |
| (shots)s                | |
| (suppression)s          | |
| (time)s                 | |
| (vehicledestroyassist)s | |
| (vehicledestroyed)s     | |
| (vehiclekills)s         | |
| (vehicletime)s          | |
| (wins)s                 | Wins |
| (wl_ratio)s             | Win/Loss Ratio |


Thanks
------
- [bf3stats.com](http://bf3stats.com) for the nice API
