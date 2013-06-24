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
from deps.NetworkTenVideo import NetworkTenVideo

# Un-comment for verbose debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: [%(filename)s:%(lineno)d] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class Main:
    def __init__( self ): 
        # parse arguments and init ten client
        params = self._parse_argv()
        self.tenClient = NetworkTenVideo(token=params['token'])
        
        # get playlist
        if params['playlistId'] == "default":
            playlist = self.tenClient.getRootPlaylist()
        else:
            playlist = self.tenClient.getPlaylist(params['playlistId'])
        
        # extract tags and use playlist code for path (used for tracking)
        tags = self.tenClient.parsePlaylistForTags(playlist)
        if (tags.has_key('playlist:code')):
            params['path'] += tags['playlist:code'] + '/'
        
        # check if the playlist has children, and display them if so
        if (type(playlist['childPlaylists']) != str and len(playlist['childPlaylists']['playlist'])>0):
            for childPlaylist in playlist['childPlaylists']['playlist']:
                xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=xbmcgui.ListItem(self._parse_title(childPlaylist['title'])),url="%s?playlistId=%s&path=%s&token=%s" % ( sys.argv[0], childPlaylist['id'], params['path'], self.tenClient.getToken()), isFolder=True, totalItems=len(playlist['childPlaylists']['playlist']))
        elif (type(playlist['mediaList']) != str and len(playlist['mediaList']['media'])>0):
            for item in playlist['mediaList']['media']:
                listitem = xbmcgui.ListItem(item['title'],thumbnailImage=item['imagePath'] + 'cropped/128x72.png')
                listitem.setInfo( "video", {'title': item['title'], 'studio': item['creator'], 'plot': item['description']} )
                xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=listitem,url="%s?mediaIds=%s&path=%s&token=%s" % ( sys.argv[0], item['id'], params['path'], self.tenClient.getToken()), totalItems=len(playlist['mediaList']['media']))
            
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
        
    def _parse_argv( self ):
        try:
            # parse sys.argv for params and return result
            params = dict( urllib.unquote_plus( arg ).split( "=" ) for arg in sys.argv[ 2 ][ 1 : ].split( "&" ) )
        except:
            # no params passed
            params = { "playlistId": "default"}
        if not params.has_key('path'):
            params['path'] = ''
        if not params.has_key('token'):
            params['token'] = None
        print repr(params)
        return params
        
    def _parse_title( self, title ):
        split = title.split('|',1)
        if (len(split) == 2):
            return split[1].strip()
        else:
            return title.strip()