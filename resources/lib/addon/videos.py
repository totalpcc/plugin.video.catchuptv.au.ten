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
import re
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
            if hasattr(listitem, 'addStreamInfo'):
                # we don't actually know the stream parameters yet, but we can guess
                listitem.addStreamInfo('video', {
                    'codec': 'h264',
                    'width': 944,
                    'height': 528,
                    'duration': float(video.length / 1000)
                })
                listitem.addStreamInfo('audio', {
                    'codec': 'aac',
                    'language': 'en',
                    'channels': 2
                })
            listitem.setProperty('IsPlayable', 'true')
            if show and show.fanart:
                listitem.setProperty('fanart_image', show.fanart)
            xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), listitem=listitem, url="%s?%s" % ( sys.argv[0], urllib.urlencode(urlArgs)), totalItems=len(videos.items), isFolder=False)

        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_EPISODE ) 
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_TITLE ) 
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME ) 
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=1 )
        xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content='episodes' )

    def _get_xbmc_list_item_info(self, video):
        info_dict = {
            'title': video.name, 
            'dateadded': video.publishedDate.strftime('%Y-%m-%d %h:%m:%s')
        }

        if video.shortDescription:
            info_dict['plot'] = video.shortDescription
            info_dict['plotoutline'] = video.shortDescription

        if video.longDescription:
            info_dict['plot'] = video.longDescription

        m = re.match('(.+?)\s*-\s*S(\d+?)\s*Ep\.?\s*(\d+?)', video.name)
        if m:
            regex_dict = {'tvshowtitle': m.group(1), 'season': m.group(2), 'episode': m.group(3)}
            info_dict.update(regex_dict)
            utils.log('Found video info from regex: %s' % repr(regex_dict))

        if 'tv_show' in video.customFields:
            info_dict['tvshowtitle'] = video.customFields['tv_show']
        if 'tv_season' in video.customFields:
            info_dict['season'] = video.customFields['tv_season']
        if 'tv_channel' in video.customFields:
            info_dict['studio'] = video.customFields['tv_channel']

        return info_dict
