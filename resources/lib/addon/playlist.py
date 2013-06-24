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
import xbmcgui
import xbmcplugin
import utils
from NetworkTenVideo import NetworkTenVideo

# Un-comment for verbose debugging
utils.handle_logger(logging.getLogger())

class Main:
    def __init__( self, params ): 
        # parse arguments and init ten client
        token = None
        if ('token' in params):
            token = params['token'][0]
        self.tenClient = NetworkTenVideo()
        
        # get playlist
        if not 'playlistId' in params or not params['playlistId'] or params['playlistId'] == "default":
            playlist = self.tenClient.getRootPlaylist()
        else:
            playlist = self.tenClient.getPlaylist(params['playlistId'][0])
        
        # get existing path
        if 'path' in params:
            path = params['path'][0]
        else:
            path = ''

        # extract tags and use playlist code for path (used for tracking)
        tags = self.tenClient.parsePlaylistForTags(playlist)
        logging.debug('Playlist Tags: %s' % repr(tags))
        if 'playlist:code' in tags:
            logging.debug('adding playlist code to path: %s' % tags['playlist:code'])
            path += tags['playlist:code'] + '/'
        
        urlArgs = {
            'path': path,
            'token': self.tenClient.getToken()
        }

        if 'advertisingConfig' in playlist:
            if playlist['advertisingConfig']['advertisingPolicy']['initialMedia'] != 'm':
                urlArgs['adConfigUrl'] = playlist['advertisingConfig']['url']
                urlArgs['showAds'] = '1'
            else:
                urlArgs['showAds'] = '0'

        # check if the playlist has children, and display them if so
        if (type(playlist['childPlaylists']) != str and len(playlist['childPlaylists']['playlist'])>0):
            for childPlaylist in playlist['childPlaylists']['playlist']:
                urlArgs['playlistId'] = childPlaylist['id']
                xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=xbmcgui.ListItem(self._parse_title(childPlaylist['title'])),url="%s?action=playlist&%s" % ( sys.argv[0], urllib.urlencode(urlArgs)), isFolder=True, totalItems=len(playlist['childPlaylists']['playlist']))
        elif (type(playlist['mediaList']) != str and len(playlist['mediaList']['media'])>0):
            for item in playlist['mediaList']['media']:
                listitem = xbmcgui.ListItem(item['title'],thumbnailImage=item['imagePath'] + 'cropped/128x72.png')
                listitem.setInfo( "video", {'title': item['title'], 'studio': item['creator'], 'plot': item['description']} )
                listitem.setProperty('IsPlayable', 'true')
                urlArgs['mediaIds'] = item['id']
                xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=listitem,url="%s?action=download&%s" % ( sys.argv[0], urllib.urlencode(urlArgs)), totalItems=len(playlist['mediaList']['media']))
            
            # episode part stacking disabled until we can figure out how to call python in between parts to refresh the auth token
            # parse the playlist for episodes then loop through the reverse sorted items array
            #episodes = self.tenClient.parsePlaylistForEpisodes(playlist)
            #for episode in sorted(episodes.items(),reverse=True):
            #    curEpisode = episode[1]
            #    print repr(curEpisode)
            #    
            #    # extract the mediaIds for the episode
            #    mediaIds = ''
            #    for i in sorted(curEpisode['media']):
            #        mediaIds += curEpisode['media'][i]['id'] + ','
            #    mediaIds = mediaIds[0:-1] # truncate last comma
            #    
            #    # add directory item
            #    listitem = xbmcgui.ListItem(self._parse_title(curEpisode['title']))
            #    listitem.setInfo( "video", {'title': curEpisode['title']} )
            #    xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=listitem,url="%s?mediaIds=%s&path=%s&token=%s" % ( sys.argv[0], mediaIds, params['path'], self.tenClient.getToken()), totalItems=len(episodes))
            
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=1 )
        
    def _parse_title( self, title ):
        split = title.split('|',1)
        if (len(split) == 2):
            return split[1].strip()
        else:
            return title.strip()