"""
    Plugin for streaming Channel Ten Videos
"""

# main imports
import sys

# plugin constants (not used)
__plugin__ = "Channel Ten CatchUp TV Video Player"
__pluginid__ = "plugin.video.catchuptv.au.ten"
__author__ = "adammw111"
__url__ = "http://xbmc-catchuptv-au.googlecode.com/"
__svn_url__ = "http://xbmc-catchuptv-au.googlecode.com/svn/"
__useragent__ = "xbmcCatchUpTV/0.1"
__credits__ = "Team XBMC"
__version__ = "0.1.0"
__svn_revision__ = "$Revision: 1 $"
__XBMC_Revision__ = "31542"


if ( __name__ == "__main__" ):
    if ( not sys.argv[ 2 ] ):
        import resources.lib.menulist as plugin
        plugin.Main()
    elif ( sys.argv[ 2 ].startswith( "?menuId=" ) ):
        import resources.lib.menu as plugin
        plugin.Main()
    elif ( sys.argv[ 2 ].startswith( "?playlistId=" ) ):
        import resources.lib.playlist as plugin
        plugin.Main()
    elif ( sys.argv[ 2 ].startswith( "?downloadId=" ) ):
        import resources.lib.download as download
        download.Main()
    elif ( sys.argv[ 2 ].startswith( "?settings=" ) ):
        import os
        import xbmc
        import xbmcaddon
        # open settings
        xbmcaddon.Addon( id=os.path.basename( os.getcwd() ) ).openSettings()
        # refresh listing in case settings changed
        xbmc.executebuiltin( "Container.Refresh" )
