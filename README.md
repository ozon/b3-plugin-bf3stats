BF3stats Plugin for Big Brother Bot
===================================
Display stats from [bf3stats.com](http://bf3stats.com) ingame.

Installation
------------
1. install the [bf3stats python module](https://github.com/ozon/python-bf3stats)
 - `easyinstall -U bf3stats` or down the [bf3stats module](https://github.com/ozon/python-bf3stats/zipball/master) and copy the folder `bf3stats` in your b3 plugin folder

2. install this plugin
 - copy the contents of extplugins to b3/extplugins/
 - add `<plugin name="bf3stats" config="@b3/extplugins/conf/plugin_bf3stats.xml"/>` in you main b3 config file

Usage
-----
Use the command `!bf3stats` ingame to display short stats.

Notes
-----
__This is still alpha stuff!__

Thanks
------
- [bf3stats.com](http://bf3stats.com) for the nice API
