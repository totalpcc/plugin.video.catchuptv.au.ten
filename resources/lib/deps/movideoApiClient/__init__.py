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
from RestClient import RestClient
__all__ = ["movideoApiClient"]

class movideoApiClient:
    _rest_url = string.Template('http://api.v2.movideo.com/rest/${method}?${params}')
    def __init__(self, application_alias, api_key, headers={}, token=None):
        logging.debug('Creating movideoApiClient class')
        self.application_alias = application_alias
        self.api_key = api_key
        self.headers = headers
        # Load RestClient
        self.rest_client = RestClient(self._rest_url, self.headers)
        
        # Load sub-modules
        from Application import Application
        self.Application = Application(self)
        logging.debug('movideoApiClient.Application loaded')
        from Playlist import Playlist
        self.Playlist = Playlist(self)
        logging.debug('movideoApiClient.Playlist loaded')
        from Media import Media
        self.Media = Media(self)
        logging.debug('movideoApiClient.Media loaded')
        
        # Get token
        if (token == None):
            self.token = self._getToken()
        else:
            self.token = token
        logging.debug('Using token %s' % repr(self.token))
        
        logging.debug('movideoApiClient init completed')
        
    def _getToken(self):
        data = self._makeRequest('session',{'applicationalias': self.application_alias, 'key': self.api_key})['session']
        return data.token
        
    def _makeRequest(self, method, params = {}):
        reqParams = {'method': method, 'params': params}
        try:
            reqParams['params']['token'] = self.token
        except AttributeError:
            pass
        return self.rest_client.request(reqParams)