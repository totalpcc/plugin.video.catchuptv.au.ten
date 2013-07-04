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
import urlparse
import urllib
import xbmcgui
import xbmcplugin
import utils
from networktenvideo.api import NetworkTenVideo
from brightcove.core import get_item
from networktenvideo.objects import Show

class Main:
    def __init__( self, params ): 
        self.client = NetworkTenVideo()

        if 'show' in params:
            show = pickle.loads(params['show'][0])
        else:
            show = None

        query = urlparse.parse_qs(params['query'][0])
        videos = self.client.search_videos(**query)
        urlArgs = {'action': 'play'}
        for video in videos.items:
            urlArgs['videoId'] = video.id
            utils.log('Adding video %s' % video)
            listitem = xbmcgui.ListItem( video.name, thumbnailImage=video.videoStillURL )
            listitem.setInfo( "video", self._get_xbmc_list_item_info(video))
            listitem.addStreamInfo('video', {'duration': video.length / 1000})
            listitem.setProperty('IsPlayable', 'true')
            if show and show.fanart:
                listitem.setProperty('fanart_image', show.fanart)
            xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), listitem=listitem, url="%s?%s" % ( sys.argv[0], urllib.urlencode(urlArgs)), totalItems=len(videos.items))

        xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content='episodes' )
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=1 )

    def _get_xbmc_list_item_info(self, video):
        info_dict = {
            'title': video.name, 
            'description': video.shortDescription,
            'dateadded': video.publishedDate.strftime('%Y-%m-%d %h:%m:%s')
        }

        if 'tv_show' in video.customFields:
            info_dict['tvshowtitle'] = video.customFields['tv_show']
        if 'tv_season' in video.customFields:
            info_dict['season'] = video.customFields['tv_season']
