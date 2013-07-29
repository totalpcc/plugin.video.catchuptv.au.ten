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
    super(Module, self).__init__('plugin.video.catchuptv.au.ten.showlist')

    # decorators
    self.showlist = self.route('/')(self.showlist)

  def showlist(self):
    api = APICache(self.plugin)

    shows = []
    for show in api.get_shows():
      item = ListItem.from_dict(
        label=show.showName,
        path=self.url_for('playlist.playlist', explicit=True, show=show.showName)
      )
      if show.fanart:
        item.set_property('fanart_image', show.fanart)
      if show.logo:
        item.set_thumbnail(show.logo)
      shows.append(item)

    self.set_content('tvshows')
    self.plugin.finish(items=shows, sort_methods=[SortMethod.LABEL_IGNORE_THE])
