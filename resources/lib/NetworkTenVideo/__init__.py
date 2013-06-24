#
#   Network Ten CatchUp TV Video API Library
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

import re
import time
from movideoApiClient import movideoApiClient
from RestClient import RestClient
from channels import CHANNELS

class NetworkTenVideo:
    defaultHeaders = {
        'User-Agent': 'Mozilla/5.0 (compatible; U; en-AU) NetworkTenVideoAPIClient/0.1',
        'Referer': 'http://apps.v2.movideo.com/client/ten/main-player/flash/video_directory.swf'
        }
    movideoApplicationConfig = None
    swfUrl = 'http://apps.v2.movideo.com/player/flash/movideo_player.swf?v=1.8'
    pageUrl = 'http://ten.com.au/video-player.htm'
    vastSite = 'tendigital'
    vastPlayer = 'TEN'
    
    def __init__(self, networkId=None, headers=None, token=None):
        if (headers == None):
            headers = self.defaultHeaders
        if (networkId == None):
            networkId = 'Ten'
        self.movideoApplicationAlias, self.movideoApiKey, self.movideoRootPlaylistId = CHANNELS[networkId]
        self.movideoApiClient = movideoApiClient(application_alias=self.movideoApplicationAlias, api_key=self.movideoApiKey, headers=headers, token=token)
    
    def parsePlaylistForEpisodes(self, playlist):
        episodes = dict()
        for media in playlist['mediaList']['media']:
            # Part detection method 1
            # Look for (1/6) at END of title
            m = re.search('^(.+?)\(([0-9]+?)\/([0-9]+?)\)$',media['title'])
            if (m != None):
                title = m.group(1)
                description = media['description']
                part = m.group(2)
                totalParts = m.group(3)
            # Part detection method 2
            # Look for (1/6) at START of description
            else:
                m = re.search('^\(([0-9]+?)\/([0-9]+?)\)(.*)$',media['description'])
                if (m != None):
                    title = media['title']
                    description = m.group(3)
                    part = m.group(1)
                    totalParts = m.group(2)
                else:
                    # Part detection method 3
                    # Look for "Part 2" or "seg 2" in title
                    m = re.search('^(.*?)(?:\s*-\s*)?(?:[pP]art|seg)\s+?([0-9]+)(.*?)$',media['title'])
                    if (m != None):
                        title = m.group(1) + " " + m.group(3)
                        description = media['description']
                        part = m.group(2)
                        totalParts = 0
                    # Give up detecting parts, assume only 1
                    else:
                        title = media['title']
                        description = media['description']
                        part = 1
                        totalParts = 1
            
            if not episodes.has_key(title):
                episodes[title] = dict()
                episodes[title]["mediaIds"] = list()
                episodes[title]["media"] = dict()
            episodes[title]["title"] = title.strip()
            episodes[title]["description"] = description.strip()
            episodes[title]["lastPart"] = part
            episodes[title]["totalParts"] = totalParts
            episodes[title]["media"][part] = media
        
        return episodes
        
    def parsePlaylistForTags(self, playlist):
        if (type(playlist['tags']) == str):
            return {}
        elif (type(playlist['tags']['tag']) == list):
            tags = dict()
            for tag in playlist['tags']['tag']:
                tags[tag['ns'] + ':' + tag['predicate']] = tag['value']
            return tags
        else:
            return {(playlist['tags']['tag']['ns'] + ':' + playlist['tags']['tag']['predicate']): playlist['tags']['tag']['value']}
    
    def getAds(self, path):
        if not self.movideoAdvertisingConfig: 
            self.getApplication()
        adConfigUrl = self.movideoAdvertisingConfig.url.replace('{vastSite}',self.vastSite).replace('{vastPlayer}',self.vastPlayer).replace('{mediaPath}',path).replace('{timestamp}',str(int(time.time())))
        rest = RestClient(adConfigUrl)
        return rest.request()
        
    def getApplication(self):
        self.movideoApplication = self.movideoApiClient.Application.application()
        self.movideoApplicationConfig = self.movideoApplication.applicationConfig
        self.movideoAdvertisingConfig = self.movideoApplication.advertisingConfig
        return self.movideoApplication
    
    def getApplicationConfig(self):
        self.movideoApplicationConfig = self.movideoApiClient.Application.applicationConfig()
        return self.movideoApplicationConfig
        
    def getToken(self):
        return self.movideoApiClient.token
        
    def getCombinedPartsPlaylist(self, playlistId):
        return self.parsePlaylistForEpisodes(self.getPlaylist(playlistId))
    
    def getPlaylist(self, playlistId):
        return self.movideoApiClient.Playlist.getPlaylist(playlistId, depth=1)
        
    def getRootPlaylist(self):
        return self.getPlaylist(self.movideoRootPlaylistId)
        
    def getMedia(self, mediaId):
        if not self.movideoApplicationConfig: 
            self.getApplication()
        mediaAuth = self.movideoApiClient.Media.authorise(mediaId)
        encodingProfile = mediaAuth['media']['encodingProfiles']['encodingProfile'][-1] #use last encoding profile, usually best quality
        return {'host': self.movideoApplicationConfig.connectionHostName, 'app': 'ondemand?ovpfv=2.1.4&auth=%s&aifp=1710&slist=%s' % (mediaAuth['authorisationToken']['token'], mediaAuth['authorisationToken']['url']), 'swfUrl': self.swfUrl, 'swfVfy': True, 'pageUrl': self.pageUrl, 'playpath': 'mp4:%s%s-%sx%s.f4v?null' % (mediaAuth['authorisationToken']['url'], encodingProfile['videoBitrate'], encodingProfile['width'], encodingProfile['height']), 'filename': mediaAuth['media']['filename'], 'name': mediaAuth['media']['filename'].split('.',1)[0], 'media':mediaAuth['media']}