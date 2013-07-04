#
#   Network Ten CatchUp TV Video Addon
#
#   Copyright (c) 2013 Adam Malcontenti-Wilson
# 
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
# 
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
# 
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.
#

import sys
import pickle
import urllib
import utils
import xbmcgui
import xbmcplugin

from networktenvideo.api import NetworkTenVideo


class Main:
    def __init__( self, params ): 
        self.client = NetworkTenVideo()
        shows = self.client.get_shows()
        urlArgs = {'action': 'playlist'}
        shows_sorted = sorted(shows.items, key=lambda k: k.showName.lower()) 
        for show in shows_sorted:
            urlArgs['show'] = pickle.dumps(show)
            utils.log('Found data for show: %s' % show)
            listitem = xbmcgui.ListItem( show.showName ) 
            if show.fanart:
                listitem.setProperty('fanart_image', show.fanart)
            if show.logo:
                listitem.setIconImage(show.logo)
            xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), listitem=listitem, url="%s?%s" % ( sys.argv[0], urllib.urlencode(urlArgs)), totalItems=len(shows.items), isFolder=True)

        xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content='tvshows' )
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=1 )