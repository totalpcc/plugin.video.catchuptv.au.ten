#
#   Movideo API Client Library for Python
#
#   Copyright (c) 2010 Adam Malcontenti-Wilson
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

import string
import logging

class Media:
    def __init__(self,parent):
        self.parent = parent
        self._makeRequest = parent._makeRequest
        
    def authorise(self, mediaId):
        """
            Returns a token to allow playback of a track with the CDN.
            
            Arguments:
                mediaId - required, media id number
        """
        logging.debug('Getting Media Token')
        return self._makeRequest('authorise/%s' % mediaId)['authorisation']
        
    def getMedia(self, mediaId):
        """
            Returns a single media object.
            
            Arguments:
                mediaId - required, media id number
        """
        logging.debug('Getting Media #%s' % mediaId)
        return self._makeRequest('media/%s' % mediaId)['media']
        
    def getActiveInactiveCount(self):
        """
            Returns the total number of Active and Inactive Media for the client.
        """
        logging.debug('Getting Active/Inactive Count')
        data = self._makeRequest('media/count')['count']
        self.parent.activeCount = data['active']
        self.parent.inactiveCount = data['inactive']
        logging.debug('%s Active / %s Inactive' % (data['active'] , data['inactive']))
        return data