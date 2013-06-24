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

SHOW_ADS = True

class Main:
    def __init__( self, params ): 
        # parse arguments and init ten client
        token = None
        if 'token' in params:
            token = params['token'][0]
        self.tenClient = NetworkTenVideo(token=token)
        
        # extract media ids then loop through each, adding to stack url
        mediaIds = params['mediaIds'][0].split(',')
        logging.debug('there are %s parts, will try to create a stack url' % len(mediaIds))
        mediaUrls = []
        for mediaId in mediaIds:
            # Get media and rtmp args
            media = self.tenClient.getMedia(mediaId)
            rtmpUrl = 'rtmpe://%s app=%s playpath=%s swfUrl=%s swfVfy=true pageUrl=%s' % (media['host'], media['app'], media['playpath'], media['swfUrl'], media['pageUrl'])
            logging.debug('Using rtmpe url, %s' % rtmpUrl)
            
            if SHOW_ADS and params['showAds'][0] != '0':
                # Extract media tags and create adPath
                tags = self.tenClient.parsePlaylistForTags(media['media'])
                logging.debug('Media Tags: %s' % repr(tags))
                if 'clip:code' in tags:
                    adPath = params['path'][0] + tags['clip:code']
                else:
                    adPath = params['path'][0] + media['name']
                
                # Use config url from parameters if set, otherwise leave as None to use default
                adConfigUrl = None
                if 'adConfigUrl' in params:
                    adConfigUrl = params['adConfigUrl'][0]
                    logging.debug('Using alternate ad config url: %s' % adConfigUrl)

                # Get advertisement config and find ad video url
                adConfig = self.tenClient.getAds(adPath, adConfigUrl)
                if 'Ad' in adConfig:
                    for creative in adConfig['Ad']['InLine']['Creatives']['Creative']:
                        if 'Linear' in creative and 'MediaFiles' in creative['Linear']:
                            mediaFile = creative['Linear']['MediaFiles']['MediaFile']
                            if not '_text' in mediaFile:
                                logging.debug('Multiple renditions of the same ad, blindly choosing the first one')
                                mediaFile = mediaFile[0]
                            adVideoUrl = mediaFile['_text']
                            logging.debug('Found advertisement, will show %s' % adVideoUrl)
                            mediaUrls.append(str(adVideoUrl))
                            break

            # add media url to stack
            mediaUrls.append(rtmpUrl)

        # TODO: perhaps a Playlist than a stack is better for this?
        url = 'stack://%s' % ' , '.join(mediaUrls)
        logging.debug('Final stack url, %s' % url)
        listitem = xbmcgui.ListItem(path=url)
        # make sure that the original ListItem is set to IsPlayable otherwise you will get handle errors here
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)

        #listitem = xbmcgui.ListItem(media['media']['title'], thumbnailImage=media['media']['imagePath'] + 'cropped/128x72.png')
        #xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(url, listitem)
