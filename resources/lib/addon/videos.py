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
import datetime
import time
import pickle
import urlparse
import urllib
import xbmcgui
import xbmcplugin
import utils
from HTMLParser import HTMLParser
from networktenvideo.api import NetworkTenVideo
from brightcove.core import get_item
from networktenvideo.objects import Show

htmlparser = HTMLParser()

# Work around strptime bug, ref: http://forum.xbmc.org/showthread.php?tid=112916
def strptime(date_string, format):
    try:
        return datetime.datetime.strptime(date_string, format)
    except TypeError:
        return datetime.datetime(*(time.strptime(date_string, format)[0:6]))

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
            listitem = xbmcgui.ListItem( htmlparser.unescape(video.name), thumbnailImage=video.videoStillURL )
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
            'title': htmlparser.unescape(video.name), 
            'dateadded': video.publishedDate.strftime('%Y-%m-%d %H:%M:%S')
        }

        if video.shortDescription:
            # Extract airdate from description, e.g. National News
            m = re.match(re.compile('(?:Mon|Tues?|Wed|Thu|Fri)?\s*(\d+?)/(\d+?)/(\d+?):\s*(.+)\s*', re.IGNORECASE), video.shortDescription)
            if m:
                if len(m.group(3)) == 2:
                    year = 2000 + int(m.group(3))
                else:
                    year = int(m.group(3))
                aired = datetime.date(year, int(m.group(2)), int(m.group(1))).strftime('%Y-%m-%d')
                info_dict['aired'] = aired
                utils.log('Extracted date aired from description: %s' % aired)
                info_dict['plot'] = m.group(4)
                info_dict['plotoutline'] = m.group(4)
            else:
                info_dict['plot'] = video.shortDescription
                info_dict['plotoutline'] = video.shortDescription

        if video.longDescription:
            info_dict['plot'] = video.longDescription

        if '&' in info_dict['plot']:
            info_dict['plot'] = htmlparser.unescape(info_dict['plot'])

        if '&' in info_dict['plotoutline']:
            info_dict['plotoutline'] = htmlparser.unescape(info_dict['plotoutline'])

        # Extract airdate from title, e.g. The Project
        m = re.match(re.compile('(.+?),?\s*-?\s* (?:(?:Mon|Tues?|Wed(?:nes)?|Thu(?:rs)?|Fri|Sat(?:ur)?|Sun)(?:day)?)?\s*(\d+?)?(?:st|nd|rd|th)?\s*(?:of)?\s*(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember))\s*(\d+?)?(?:st|nd|rd|th)?(?:\s+(\d+))?', re.IGNORECASE), video.name)
        if m:
            utils.log('airdate matches: title=%s, showname=%s, day=%s, month=%s, day2=%s, year=%s' % (video.name, m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)))

            day = None
            month = None
            year = None
            if m.group(2) and int(m.group(2)) != 0:
                day = int(m.group(2))
            elif m.group(4) and int(m.group(4)) != 0:
                day = int(m.group(4))

            monthName = m.group(3)
            if monthName and len(monthName) != 0:
                date = None
                try:
                    date = strptime(monthName,'%b')
                except ValueError:
                    pass
                if date is None:
                    try:
                        date = strptime(monthName,'%B')
                    except ValueError:
                        pass
                if date:
                    month = date.month

            if m.group(5) and int(m.group(5)) != 0:
                if len(m.group(5)) == 2:
                    year = 2000 + int(m.group(5))
                else:
                    year = int(m.group(5))

            if day is not None and month is not None:
                if year is None:
                    utils.log('Year not specified, assuming current year')
                    year = datetime.datetime.now().year
                aired = datetime.date(year, month, day).strftime('%Y-%m-%d')
                info_dict['aired'] = aired
                utils.log('Extracted date aired from title: %s (%s)' % (video.name, aired))

        # Extract TV Show name, Season/Episode from title
        m = re.match('(.+?)\s*-\s*S(\d+?)\s*Ep\.?\s*(\d+)', video.name)
        if m:
            regex_dict = {'tvshowtitle': m.group(1), 'season': m.group(2), 'episode': m.group(3)}
            info_dict.update(regex_dict)
            utils.log('Found video info from regex: %s' % repr(regex_dict))

        # Extract TV Show name, Season/Episode from custom fields
        if 'tv_show' in video.customFields:
            info_dict['tvshowtitle'] = video.customFields['tv_show']
        if 'tv_season' in video.customFields:
            info_dict['season'] = video.customFields['tv_season']

        if 'tv_channel' in video.customFields:
            info_dict['studio'] = video.customFields['tv_channel']
        if 'video_type_short_form' in video.customFields:
            if video.customFields['video_type_short_form'] == 'News clip':
                info_dict['genre'] = 'News'

        return info_dict
