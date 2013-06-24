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

try:
    import deps.simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        import simplejson as json

class Playlist:
    def __init__(self,parent):
        self.parent = parent
        self._makeRequest = parent._makeRequest
        
    def getPlaylist(self, playlistId, includeMedia=False, output=None, playerUrl=None, channelUrl=None, channelTitle=None, channelDescription=None, depth=None):
        """
            Return a playlist (this does not return tracks within a playlist)
            
            Arguments:
                includeMedia - boolean, retrieve media data with playlists
                output - string, either 'xml' or 'mrss'
                playerUrl - string, required for mrss
                channelUrl - string, required for mrss
                channelTitle - string, overrides defaults for mrss
                channelDescription - string, overrides defaults for mrss
        """
        # Build Params
        params = {'includeMedia':includeMedia}
        if (output != None):
            params['output'] = output
        if (playerUrl != None):
            params['playerUrl'] = playerUrl
        if (channelUrl != None):
            params['channelUrl'] = channelUrl
        if (channelTitle != None):
            params['channelTitle'] = channelTitle
        if (channelDescription != None):
            params['channelDescription'] = channelDescription
        if (depth != None):
            params['depth'] = depth    
            
        # Get Playlist
        logging.debug('Getting Playlist #%s' % playlistId)
        return self._makeRequest('playlist/%s' % playlistId, params)['playlist']
        
    def getPlaylists(self, tagProfiles=None, orderBy=None, orderDesc=False, orderValue=None, paged=False, page=None, pageSize=None, totals=False, includeMedia=False):
        """
            Returns all the playlists associated with the client
            
            Arguments:
                tagProfiles - array, Tag Profile names to include in search
                orderBy - string, field to sort by, 'title', 'description', 'creationdate', 'tag'
                orderDesc - boolean, sort decending
                paged - boolean, single list or paged
                page - number, page number
                pageSize - number, results per page
                totals - boolean, only retrieve total count
                includeMedia - boolean, retrieve media data with playlists
        """
        # Build Params
        params = {'orderDesc':orderDesc, 'paged': paged, 'totals':totals, 'includeMedia':includeMedia}
        if (tagProfiles != None):
            params['tagProfiles'] = json.dumps(tagProfiles)
        if (orderBy != None):
            params['orderBy'] = orderBy
        if (page != None):
            params['page'] = page
        if (pageSize != None):
            params['pageSize'] = pageSize
        
        # Get Playlist
        logging.debug('Getting Playlists')
        return self._makeRequest('playlist', params)['list']
        
    def getPlaylistMedia(self, playlistId, output=None, playerUrl=None, channelUrl=None, channelTitle=None, channelDescription=None):
        """
            Return the media of a given playlist in order
            
            Arguments:
                playlistId - required, playlist id
                output - string, either 'xml', 'mrss' or 'googleSiteMap'
                playerUrl - string, required for mrss
                channelUrl - string, required for mrss
                channelTitle - string, overrides defaults for mrss
                channelDescription - string, overrides defaults for mrss
        """
        # Build Params
        params = {}
        if (output != None):
            params['output'] = output
        if (playerUrl != None):
            params['playerUrl'] = playerUrl
        if (channelUrl != None):
            params['channelUrl'] = channelUrl
        if (channelTitle != None):
            params['channelTitle'] = channelTitle
        if (channelDescription != None):
            params['channelDescription'] = channelDescription
        # Get Playlist
        logging.debug('Getting Playlist #%s Media' % playlistId)
        return self._makeRequest('playlist/%s/media' % playlistId, params)['list']
        
#    def getPlaylistWithMedia(self, playlistId):
#        """
#            Returns playlist metadata, including playlist media items
#            
#            Arguments:
#                playlistId - required, playlist id
#        """
#        logging.debug('Getting Playlist #%s' % playlistId)
#        return self._makeRequest('playlist/complete/%s' % playlistId)
        
    def addMediaToPlaylist(self, playlistId, mediaId, newPosition=None, originalPosition=None):
        """
            Add the specified Media to the specified Playlist
            
            Arguments:
                playlistId - required
                mediaId - required
                newPosition
                oldPosition
        """
        # Build Params
        params = {'mediaId':mediaId}
        if (newPosition != None):
            params['newPosition'] = newPosition
        if (originalPosition != None):
            params['originalPosition'] = originalPosition
        logging.debug('Adding Media #%s to Playlist #%s' % (mediaId, playlistId))
        response = self._makeRequest('playlist/%s/media/add' % playlistId, params)
        if (response == ''):
            return True
        else:
            return response #error
        
    def moveMediaInPlaylist(self, playlistId, mediaId, newPosition, originalPosition):
        """
            Move the specified Media in the specified Playlist
            
            Arguments:
                playlistId - required
                mediaId - required
                newPosition - required
                oldPosition - required
        """
        params = {'mediaId':mediaId, 'newPosition': newPosition, 'oldPosition': oldPosition}
        logging.debug('Moving Media #%s in Playlist #%s' % (mediaId, playlistId))
        response = self._makeRequest('playlist/%s/media/move' % playlistId, params)
        if (response == ''):
            return True
        else:
            return response #error
        
    def removeMediaFromPlaylist(self, playlistId, mediaId):
        """
            Remove the specified Media from the specified Playlist
            
            Arguments:
                playlistId - required
                mediaId - required
        """
        params = {'mediaId':mediaId}
        logging.debug('Removing Media #%s from Playlist #%s' % (mediaId, playlistId))
        response = self._makeRequest('playlist/%s/media/remove' % playlistId, params)
        if (response == ''):
            return True
        else:
            return response #error
        
    def createNewPlaylist(self, title, description=None, status='ACTIVE', syndicated=False, syndicatedPartners=None, tagProfileId=None, tags=None):
        """
            Create a new playlist
            
            Arguments:
                title - string, required
                description - string
                status - string, either 'ACTIVE' or 'INACTIVE'
                syndicated - boolean, is the playlist syndicated
                syndicatedPartners - array, client IDs
                tagProfileId - number
                tags - array, Descriptive tags
        """
        # Build Params
        params = {'title': title, 'status': status, 'syndicated': syndicated}
        if (description != None):
            params['description'] = description
        if (syndicatedPartners != None):
            params['syndicatedPartners'] = json.dumps(syndicatedPartners)
        if (tagProfileId != None):
            params['tagProfileId'] = tagProfileId
        if (tags != None):
            params['tags'] = json.dumps(tags)
        
        # Create Playlist
        logging.debug('Creating %s Playlist "%s"' % (status,title))
        return self._makeRequest('playlist/create', params)['playlist']
        
    def updateExistingPlaylist(self, playlistId, title, description=None, status='ACTIVE', syndicated=False, syndicatedPartners=None, tagProfileId=None, tags=None):
        """
            Update the specified playlist
            
            Arguments:
                playlistId - required
                title - string, required
                description - string
                status - string, either 'ACTIVE' or 'INACTIVE'
                syndicated - boolean, is the playlist syndicated
                syndicatedPartners - array, client IDs
                tagProfileId - number
                tags - array, Descriptive tags
        """
        # Build Params
        params = {'title': title, 'status': status, 'syndicated': syndicated}
        if (description != None):
            params['description'] = description
        if (syndicatedPartners != None):
            params['syndicatedPartners'] = json.dumps(syndicatedPartners)
        if (tagProfileId != None):
            params['tagProfileId'] = tagProfileId
        if (tags != None):
            params['tags'] = json.dumps(tags)
        
        # Create Playlist
        logging.debug('Updating %s Playlist "%s"' % (status,title))
        return self._makeRequest('playlist/update/%s' % playlistId, params)['playlist']
        
    def deletePlaylist(self, playlistId):
        """
            Delete the specified playlist
            
            Arguments:
                playlistId - required
        """
        logging.debug('Deleting Playlist #%s' % playlistId)
        return self._makeRequest('playlist/delete/%s' % playlistId)
        
    def searchPlaylist(self, tags=None, excludeTags=None, keyword=None, title=None, description=None, tagProfiles=None, tagOperator=None, operator=None, excludeOperator=None, keywordOperator=None, paged=False, page=None, pageSize=None, totals=False, orderBy=None, orderDesc=False, orderValue=None, output=None, playerUrl=None, channelUrl=None, channelTitle=None, channelDescription=None):
        """
            Search for a playlist by the given parameters
            
            Arguments:
                tags - array, descriptive tags to search for
                excludeTags - array, descriptive tags to exclude
                keyword - string, keyword to search against title or description
                title - string, keyword to search against title only
                description - string, keyword to search against description only
                tagProfiles - array, tag profile names to include in search
                tagOperator - string, operator between each tag in search block supplied by tags ("AND", "OR")
                operator - string, operator between each search block supplied by tags ("AND", "OR", "RANGE")
                excludeOperator - string, operator between each exclude in search block supplied by tags ("AND", "OR", "RANGE")
                keywordOperator - string, operator between each keyword in search block supplied by tags ("AND", "OR")
                paged - boolean, if results should be paged or a single list
                page - number, page number
                pageSize - number, page size
                totals - boolean, only retrieve total count
                orderBy - string, order by field based on what to retrieve ('title','description','creationdate','tag)
                orderDesc - boolean, sort descending
                orderValue - string, namespace and predicate of the full machine tag to order by (Required when orderBy is by tag field)
                output - string, output type: 'xml' or 'mrss'
                playerUrl - string, url of player that will appear in the mrss feed, required for mrss output
                channelUrl - string, url of mrss channel, required for mrss output 
                channelTitle - string, override title of mrss channel
                channelDescription - string, override description of mrss channel
        """
        # Build Params
        params = {'paged':paged, 'totals':totals, 'orderDesc':orderDesc}
        if (tags != None):
            params['tags'] = json.dumps(tags)
        if (excludeTags != None):
            params['excludeTags'] = json.dumps(excludeTags)
        if (keyword != None):
            params['keyword'] = keyword
        if (title != None):
            params['title'] = title
        if (description != None):
            params['description'] = description
        if (tagProfiles != None):
            params['tagProfiles'] = json.dumps(tagProfiles)
        if (tagOperator != None):
            params['tagOperator'] = tagOperator
        if (operator != None):
            params['operator'] = operator
        if (excludeOperator != None):
            params['excludeOperator'] = excludeOperator
        if (keywordOperator != None):
            params['keywordOperator'] = keywordOperator
        if (page != None):
            params['page'] = page
        if (pageSize != None):
            params['pageSize'] = pageSize
        if (orderBy != None):
            params['orderBy'] = orderBy
        if (orderValue != None):
            params['orderValue'] = orderValue
        if (output != None):
            params['output'] = output
        if (playerUrl != None):
            params['playerUrl'] = playerUrl
        if (channelUrl != None):
            params['channelUrl'] = channelUrl
        if (channelTitle != None):
            params['channelTitle'] = channelTitle
        if (channelDescription != None):
            params['channelDescription'] = channelDescription
        
        # Perform search request
        logging.debug('Searching for Playlist')
        return self._makeRequest('playlist/search', params)['list']