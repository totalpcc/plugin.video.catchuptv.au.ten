#
#   Network Ten CatchUp TV Video Addon
#
#   Copyright (c) 2014 Adam Malcontenti-Wilson
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

class Module(xbmcswift2.Module):
  def __init__(self):
    super(Module, self).__init__('plugin.video.catchuptv.au.ten.menu')

    # decorators
    self.menu = self.route('/')(self.menu)

  def menu(self):
    items = [
        {'label': 'Featured', 'path': self.plugin.url_for('videolist.videolist', query='featured', page='0')},
        {'label': 'TV Shows', 'path': self.plugin.url_for('showlist.showlist', type='tvshows')},
        {'label': 'News', 'path': self.plugin.url_for('showlist.showlist', type='news')},
        {'label': 'Sport', 'path': self.plugin.url_for('showlist.showlist', type='sport')},
        {'label': 'Live Streaming', 'path': self.plugin.url_for('showlist.showlist', type='live')}
    ]
    return items
