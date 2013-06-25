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
import datetime
import urllib
import xbmcgui
import xbmcplugin
import utils
from NetworkTenVideo import NetworkTenVideo

PART_STACKING = True

utils.handle_logger(logging.getLogger())

class Main:
    def __init__( self, params ): 
        # parse arguments and init ten client
        token = None
        if 'token' in params:
            token = params['token'][0]
        self.tenClient = NetworkTenVideo(token=token)
        
        # get playlist
        if not 'playlistId' in params or not params['playlistId'] or params['playlistId'] == "default":
            playlist = self.tenClient.getRootPlaylist()
        else:
            playlist = self.tenClient.getPlaylist(params['playlistId'][0])
        logging.debug('Playlist: %s' % repr(playlist))
        
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
            urlArgs['showAds'] = playlist['advertisingConfig']['advertisingPolicy']['initialMedia'].count('a')

        # check if the playlist has children, and display them if so
        if (type(playlist['childPlaylists']) != str and len(playlist['childPlaylists']['playlist'])>0):
            def display_child_playlist( childPlaylist, total ):
                title = self._parse_title(childPlaylist['title'])
                childTags = self.tenClient.parsePlaylistForTags(childPlaylist)
                logging.debug('Found child playlist "%s" with tags: %s' % (title, repr(childTags)))
                
                if not 'external:link' in childTags:
                    urlArgs['playlistId'] = childPlaylist['id']

                    if 'Full Episodes' in title:
                        urlArgs['listType'] = 'episodes'
                    else:
                        urlArgs['listType'] = 'tvshows'
                    listitem = xbmcgui.ListItem(title)
                    if 'description' in childPlaylist:
                        listitem.setInfo('video', { 'plot' : childPlaylist['description'] })
                    xbmcplugin.addDirectoryItem( handle=int( sys.argv[ 1 ] ), listitem=listitem, url="%s?action=playlist&%s" % ( sys.argv[0], urllib.urlencode(urlArgs)), isFolder=True, totalItems=total)
                else:
                    logging.debug('Ignoring playlist "%s" as contains external:link=%s' % (title, childTags['external:link']))

            if (type(playlist['childPlaylists']['playlist']) == list):
                for childPlaylist in playlist['childPlaylists']['playlist']:
                    display_child_playlist(childPlaylist, len(playlist['childPlaylists']['playlist']))
            else:
                display_child_playlist(playlist['childPlaylists']['playlist'], 1)

        elif (type(playlist['mediaList']) != str and len(playlist['mediaList']['media'])>0):
            if PART_STACKING:
                # parse the playlist for episodes then loop through the reverse sorted items array
                episodes = self.tenClient.parsePlaylistForEpisodes(playlist)
                for episode in sorted(episodes.items(),reverse=True):
                    title = episode[0]
                    curEpisode = episode[1]
                    media = curEpisode['media']
                    mediaIds = []
                    duration = 0.0
                    firstMedia = media[media.keys()[0]]
                    logging.debug('Found episode: %s, %s media items' % (title, len(media)))

                    for i in sorted(curEpisode['media']):
                        mediaIds.append(curEpisode['media'][i]['id'])
                        duration += float(curEpisode['media'][i]['duration'])

                    listitem = xbmcgui.ListItem(curEpisode['title'], thumbnailImage=firstMedia['imagePath'] + '600x338.jpg')
                    listitem.setInfo('video', self._get_xbmc_list_item(title, curEpisode['description'], firstMedia))
                    listitem.setProperty('IsPlayable', 'true')
                    listitem.addStreamInfo('video', {'duration': duration})
                    urlArgs['mediaIds'] = ','.join(mediaIds)
                    xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=listitem,url="%s?action=download&%s" % ( sys.argv[0], urllib.urlencode(urlArgs)), totalItems=len(episodes))
            else:
                # just add each item in the playlist individually
                for item in playlist['mediaList']['media']:
                    listitem = xbmcgui.ListItem(item['title'], thumbnailImage=item['imagePath'] + '600x338.jpg')
                    listitem.setInfo( "video", self._get_xbmc_list_item(item['title'], item['description'], item))
                    listitem.setProperty('IsPlayable', 'true')
                    listitem.addStreamInfo('video', {'duration': duration})
                    urlArgs['mediaIds'] = item['id']
                    xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=listitem,url="%s?action=download&%s" % ( sys.argv[0], urllib.urlencode(urlArgs)), totalItems=len(playlist['mediaList']['media']))

        if 'listType' in params and params['listType']:
            xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content=params['listType'][0] )
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=1 )

    def _get_xbmc_list_item( self, title, description, media ):
        info_dict = {'title': title, 'plot': description}
        tags = self.tenClient.parsePlaylistForTags(media)
        m = re.search('Ep\.?\s*([0-9]+)', title)
        if m is not None:
            info_dict['episode'] = m.group(1)
        if 'show:name' in tags:
            info_dict['tvshowtitle'] = tags['show:name']
        if 'show:genre' in tags:
            info_dict['genre'] = tags['show:genre']
        if 'show:production_number' in tags:
            info_dict['season'] = tags['show:production_number']
        if 'series:number' in tags:
            info_dict['season'] = tags['series:number']
        if 'classification:value' in tags:
            if 'consumer_advice:value' in tags:
                info_dict['mpaa'] = "%s: %s" % (tags['classification:value'], tags['consumer_advice:value'])
            else:
                info_dict['mpaa'] = tags['classification:value']
        if 'actors:name' in tags:
            info_dict['cast'] = [actor.strip() for actor in tags['actors:name'].split(',')]
        if 'show:content_owner' in tags:
            info_dict['studio'] = tags['show:content_owner']
        if 'mediaSchedules' in media and len(media['mediaSchedules']['mediaSchedule'])>0:
            if 'start' in media['mediaSchedules']['mediaSchedule']:
                info_dict['aired'] = media['mediaSchedules']['mediaSchedule']['start']
            else:
                info_dict['aired'] = media['mediaSchedules']['mediaSchedule'][0]['start']
        return info_dict
        
    def _parse_title( self, title ):
        split = title.split('|',1)
        if (len(split) == 2):
            return split[1].strip()
        else:
            return title.strip()
