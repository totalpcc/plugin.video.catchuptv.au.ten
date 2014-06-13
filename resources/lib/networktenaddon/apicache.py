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

import config
from networktenvideo.api import NetworkTenVideo

try:
  import simplejson as json
except ImportError:
  try:
    import deps.simplejson as json
  except ImportError:
    import json

class APICache:
  def __init__(self, plugin=None):
    self.api = NetworkTenVideo()
    self.log = plugin.log
    self.log.debug('Cache TTL set to %d minutes', config.CACHE_TTL)
    self.cache = plugin.get_storage('showlist', TTL=config.CACHE_TTL)
    print repr(self.cache)

  def get_show(self, show, bypassCache=False):
    if not bypassCache and 'showlist' in self.cache and show in self.cache['showlist']:
      self.log.debug('Retrieving show data for show "%s" from cache...', show)
      show_data = self.cache['showlist'][show]
    else:
      self.log.debug('Retrieving show data for show "%s" from api ...', show)
      show_data = self.api.get_show(show)
      if not 'showlist' in self.cache:
        self.cache['showlist'] = {}
      self.cache['showlist'][show_data.showName] = show_data
      self.cache.sync()

    self.log.debug('Show data: %s', repr(show_data))

    return show_data

  def get_shows(self, bypassCache=False):
    if not bypassCache and 'showlist' in self.cache:
      self.log.debug('Retrieving show list from cache...')
      shows = self.cache['showlist'].values()
    else:
      self.log.debug('Retrieving show list from api...')
      shows = self.api.get_shows().items
      if not 'showlist' in self.cache:
        self.cache['showlist'] = {}
      for show in shows:
        self.cache['showlist'][show.showName] = show
      self.cache.sync()

    self.log.debug('Shows: %s', repr(shows))

    return shows

  def get_playlists(self, show, bypassCache=False):
    if not bypassCache and 'showlist' in self.cache and show in self.cache['showlist'] and self.cache['showlist'][show].playlists and len(self.cache['showlist'][show].playlists) > 0:
      self.log.debug('Retrieving playlists for show "%s" from cache...', show)
      playlists = self.cache['showlist'][show].playlists
    else:
      self.log.debug('Retrieving playlists for show "%s" from api...', show)
      playlists = self.api.get_playlists_for_show(show).items
      if show in cache['showlist']:
        self.cache['showlist'][show].playlists = playlists
        self.cache.sync()

    self.log.debug('Playlists: %s', repr(playlists.items))

    return playlists

  def search_videos(self, bypassCache=False, **kwargs):
    key = json.dumps(kwargs)
    print repr(key)
    if not bypassCache and 'searches' in self.cache and key in self.cache['searches']:
      self.log.debug('Using search results from cache...')
      result = self.cache['searches'][key]
    else:
      self.log.debug('Using search results from api...')
      result = self.api.search_videos(**kwargs)
      if not 'searches' in self.cache:
        self.cache['searches'] = {}
      self.cache['searches'][key] = result
      self.cache.sync()
    return result
