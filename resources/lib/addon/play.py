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
import urllib
import xbmc
import xbmcgui
import xbmcplugin
import utils
from networktenvideo.api import NetworkTenVideo, SWF_URL, PAGE_URL

class Main:
    def __init__( self, params ): 
        self.client = NetworkTenVideo()
        media = self.client.get_media_for_video(params['videoId'][0])
        utils.log('Found media renditions for video: %s' % repr(media.items))

        # Blindly go for the highest bitrate for now. Later versions could include a customisable setting of which stream to use
        media_sorted = sorted(media.items, key=lambda m: m.encodingRate, reverse=True)
        media = media_sorted[0]
        path = media.defaultURL
        if path.startswith('rtmp'):
            path = path.replace('&mp4:', ' playpath=mp4:')
            path += ' swfVfy=true swfUrl=%s pageUrl=%s' % (SWF_URL, PAGE_URL)
        utils.log('Using rendition: %s with url: %s' % (media, path))

        listitem = xbmcgui.ListItem(path=path)
        if hasattr(listitem, 'addStreamInfo'):
            listitem.addStreamInfo('video', {'codec': media.videoCodec, 'width': media.frameWidth, 'height': media.frameHeight})
        # make sure that the original ListItem is set to IsPlayable otherwise you will get handle errors here
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)
