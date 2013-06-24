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
import logging
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import utils
from NetworkTenVideo import NetworkTenVideo

utils.handle_logger(logging.getLogger())

class Main:
    def __init__( self ): 
        # parse arguments and init ten client
        params = self._parse_argv()
        self.tenClient = NetworkTenVideo(token=params['token'])
        
        # extract media ids then loop through each, adding to stack url
        mediaIds = params['mediaIds'].split(',')
        print 'DEBUG: there are %s parts, will try to create a stack url' % len(mediaIds)
        url = 'stack://'
        for mediaId in mediaIds:
            # Get media and rtmp args
            media = self.tenClient.getMedia(mediaId)
            rtmpUrl = 'rtmpe://%s app=%s playpath=%s swfUrl=%s swfVfy=true pageUrl=%s' % (media['host'], media['app'], media['playpath'], media['swfUrl'], media['pageUrl'])
            print 'Using rtmpe url, %s' % rtmpUrl
            
            # Extract media tags and create adPath
            tags = self.tenClient.parsePlaylistForTags(media['media'])
            print repr(tags)
            if (tags.has_key('clip:code')):
                adPath = params['path'] + tags['clip:code']
            else:
                adPath = params['path'] + media['name']
            
            # Get advertisement
            adConfig = self.tenClient.getAds(adPath)
            adUrl = adConfig['VideoAdServingTemplate']['Ad']['InLine']['Video']['MediaFiles']['MediaFile']['URL']
            print 'Found advertisement, will show %s' % adUrl
            
            # add urls to stack
            url += adUrl + ' , ' + rtmpUrl + ' , '
        url = url[0:-3] # remove last comma from stack
        print 'Final stack url, %s' % url
        xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(url, xbmcgui.ListItem(media['media']['title'], thumbnailImage=media['media']['imagePath'] + 'cropped/128x72.png'))
        
    def _parse_argv( self ):
        try:
            # parse sys.argv for params and return result
            params = dict( urllib.unquote_plus( arg ).split( "=" ) for arg in sys.argv[ 2 ][ 1 : ].split( "&" ) )
        except:
            # no params passed
            params = {}
        if not params.has_key('path'):
            params['path'] = ''
        if not params.has_key('token'):
            params['token'] = None
        print repr(params)
        return params