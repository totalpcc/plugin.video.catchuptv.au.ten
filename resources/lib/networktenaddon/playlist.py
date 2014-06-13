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

import xbmcswift2
from xbmcswift2 import ListItem, SortMethod
from apicache import APICache

class Module(xbmcswift2.Module):
  def __init__(self):
    super(Module, self).__init__('plugin.video.catchuptv.au.ten.playlist')
    
    # decorators
    self.playlist = self.route('/playlists/<show>')(self.playlist)

  def playlist(self, show):
    api = APICache(self.plugin)
    show_data = api.get_show(show)

    if len(show_data.playlists) > 0:
      playlists = show_data.playlists
    else:
      playlists = api.get_playlists(show)

    playlistItems = []
    for playlist in playlists:
      item = ListItem.from_dict(
        label=playlist.name,
        path=self.url_for('videolist.videolist', explicit=True, query=playlist.query, show=show)
      )
      if show_data.fanart:
        item.set_property('fanart_image', show_data.fanart)
      if playlist.type == "season":
        item.set_info('video', {season: playlist.season})
      playlistItems.append(item)

    self.plugin.finish(items=playlistItems, sort_methods=[SortMethod.UNSORTED, SortMethod.LABEL_IGNORE_THE])
