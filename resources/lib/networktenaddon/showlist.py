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
import config
import time
import urllib
import urlparse
from networktenvideo.api import NetworkTenVideo

class Module(xbmcswift2.Module):
  def __init__(self):
    super(Module, self).__init__('plugin.video.catchuptv.au.ten.showlist')

    # decorators
    self.showlist = self.route('/shows/<type>')(self.showlist)

  def showlist(self, type):
    api = NetworkTenVideo(self.plugin.cached(TTL=config.CACHE_TTL))
    shows = []
    if 'news' == type:
      for news in api.get_news():
        fanart_url = api.get_fanart(news)

        item = ListItem.from_dict(
          label=news['Title'],
          path=self.url_for('videolist.videolist', explicit=True, query=news['BCQueryForVideoListing'], page='0', fanart=fanart_url),
        )

        if fanart_url:
          item.set_property('fanart_image', fanart_url)

        if 'Thumbnail' in news:
          url = news['Thumbnail']
          if url.startswith('//'):
            url = 'http:' + url
          item.set_thumbnail(url)
        shows.append(item)
    elif 'sport' == type:
      for sport in api.get_sports():
        item = ListItem.from_dict(
          label=sport['Title'],
          path=self.url_for('videolist.videolist', explicit=True, query=sport['BCQueryForVideoListing'], page='0'),
        )
        shows.append(item)
    elif 'live' == type:
      for category in api.get_live_categories():
        fanart_url = None

        if 'fanart' in category:
          fanart_url = category['fanart']

        item = ListItem.from_dict(
          label=category['title'],
          path=self.url_for('videolist.videolist', explicit=True, query=category['query'], page='0', fanart=fanart_url),
        )

        if fanart_url:
          item.set_property('fanart_image', fanart_url)

        if 'thumbnail' in category:
          item.set_thumbnail(category['thumbnail'])

        shows.append(item)
    else: #tvshows
      for show in api.get_shows():
        info_dict = {}
        if show['IsLongFormAvailable'] is not True: #todo: make this a setting
          continue
        if 'Genres' in show and len(show['Genres']):
          info_dict['genre'] = show['Genres'][0]['Name']
        if 'Description' in show:
          info_dict['plot'] = show['Description']
        if 'CurrentSeasonFirstEpisodeAirDateTime' in show:
          try:
            date = time.strptime(show['CurrentSeasonFirstEpisodeAirDateTime'],'%d-%m-%Y %H:%M:%S %p')
            info_dict['aired'] = time.strftime('%Y-%m-%d', date)
            info_dict['premiered'] = time.strftime('%Y-%m-%d', date)
            info_dict['year'] = time.strftime('%Y', date)
          except Exception, e:
            pass
        if 'Channel' in show:
          info_dict['studio'] = show['Channel']
        if 'NumberOfVideosFromBCQuery' in show:
          # not technically correct as this also returns the number of short form as well but close enough
          info_dict['episode'] = show['NumberOfVideosFromBCQuery']

        if 'BCQueryForVideoListing' in show and len(show['BCQueryForVideoListing']):
          query = urlparse.parse_qs(show['BCQueryForVideoListing'], True)
          if 'all' not in query:
            query['all'] = []
          elif not isinstance(query['all'], list):
            query['all'] = [ query['all'] ]
          query['all'].append('video_type_long_form:Full Episode')
        else:
          continue

        fanart_url = api.get_fanart(show)

        item = ListItem.from_dict(
          label=show['Title'],
          path=self.url_for('videolist.videolist', explicit=True, query=urllib.urlencode(query, True), fanart=fanart_url), #ShowPageItemId=show['ShowPageItemId']
          info=info_dict
        )

        if fanart_url:
          item.set_property('fanart_image', fanart_url)

        if 'Thumbnail' in show:
          url = show['Thumbnail']
          if url.startswith('//'):
            url = 'http:' + url
          item.set_thumbnail(url)
        shows.append(item)

    self.set_content('tvshows')
    self.plugin.finish(items=shows, sort_methods=[SortMethod.LABEL_IGNORE_THE])
