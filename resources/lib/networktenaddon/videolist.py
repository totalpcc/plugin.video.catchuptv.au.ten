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

import re
import datetime
import time
import urlparse
import xbmcswift2
import config
from HTMLParser import HTMLParser
from xbmcswift2 import ListItem, SortMethod
from networktenvideo.api import NetworkTenVideo

htmlparser = HTMLParser()

# Work around strptime bug, ref: http://forum.xbmc.org/showthread.php?tid=112916
def strptime(date_string, format):
    try:
        return datetime.datetime.strptime(date_string, format)
    except TypeError:
        return datetime.datetime(*(time.strptime(date_string, format)[0:6]))

class Module(xbmcswift2.Module):
  def __init__(self):
    super(Module, self).__init__('plugin.video.catchuptv.au.ten.videolist')

    # decorators
    self.videolist = self.route('/videos/<query>/<page>', options={'page': '0'})(self.videolist)

  def videolist(self, query, page='0'):
    api = NetworkTenVideo(self.plugin.cached(TTL=config.CACHE_TTL))
    if query == 'featured':
      homepage = api.get_homepage()
      videoIds = []
      for item in homepage:
        videoIds.append(item['brightcoveid'])
      videos = api.find_videos_by_ids(video_ids = videoIds)
    else:
      querystring = query
      query = urlparse.parse_qs(query)
      query['page_number'] = page
      videos = api.search_videos(**query)

    fanart_url = None
    if 'fanart' in self.request.args:
      fanart_url = self.request.args['fanart'][0]

    update_listing = False
    if 'update' in self.request.args and self.request.args['update'][0]:
      update_listing = True

    videoItems = []
    for video in videos.items:
      item = ListItem.from_dict(
        label=htmlparser.unescape(video.name),
        thumbnail=video.videoStillURL,
        is_playable=True,
        path=self.url_for('play.play', explicit=True, videoId=video.id)
      )
      item.set_info( "video", self.get_item_info(video))
      item.add_stream_info('video', {
        'codec': 'h264',
        'width': 944,
        'height': 528,
        'duration': float(video.length / 1000)
      })
      item.add_stream_info('audio', {
        'codec': 'aac',
        'language': 'en',
        'channels': 2
      })

      if fanart_url:
        item.set_property('fanart_image', fanart_url)
      videoItems.append(item)

    if videos.total_count > (videos.page_size * (int(page) + 1)):
      item = ListItem.from_dict(
        label='Next >>',
        path=self.url_for('videolist.videolist', query=querystring, page=str(int(page) + 1), fanart=fanart_url, update=True)
      )
      if fanart_url:
        item.set_property('fanart_image', fanart_url)
      videoItems.insert(0, item)

    if int(page) > 0:
      item = ListItem.from_dict(
        label='<< Previous',
        path=self.url_for('videolist.videolist', query=querystring, page=str(int(page) - 1), fanart=fanart_url, update=True)
      )
      if fanart_url:
        item.set_property('fanart_image', fanart_url)
      videoItems.insert(0, item)

    self.set_content('episodes')
    self.plugin.finish(
      items=videoItems,
      update_listing=update_listing,
      sort_methods=[SortMethod.UNSORTED, SortMethod.EPISODE, SortMethod.VIDEO_TITLE, SortMethod.VIDEO_RUNTIME])

  def get_item_info(self, video):
    info_dict = {
      'title': htmlparser.unescape(video.name),
      'dateadded': video.publishedDate.strftime('%Y-%m-%d %H:%M:%S')
    }

    if 'clip_title' in video.customFields:
      info_dict['title'] = video.customFields['clip_title']

    if 'episode_name' in video.customFields:
      info_dict['title'] += ': ' + video.customFields['episode_name']

    if 'broadcast_date_previous' in video.customFields:
      try:
        info_dict['aired'] = video.customFields['broadcast_date_previous']
      except:
        pass
    elif 'start_date_au' in video.customFields:
      try:
        info_dict['aired'] = strptime(video.customFields['start_date_au'], '%Y-%m-%d %I:%M %p').strftime('%Y-%m-%d')
      except:
        pass

    if video.shortDescription:
      # Extract airdate from description, e.g. National News
      m = re.match(re.compile('(?:Mon|Tues?|Wed|Thu|Fri)?\s*(\d+?)/(\d+?)/(\d+?):\s*(.+)\s*', re.IGNORECASE), video.shortDescription)
      if m:
        if len(m.group(3)) == 2:
          year = 2000 + int(m.group(3))
        else:
          year = int(m.group(3))
        aired = datetime.date(year, int(m.group(2)), int(m.group(1))).strftime('%Y-%m-%d')
        info_dict['aired'] = aired
        self.log.debug('Extracted date aired from description: %s' % aired)
        info_dict['plot'] = m.group(4)
        info_dict['plotoutline'] = m.group(4)
      else:
        info_dict['plot'] = video.shortDescription
        info_dict['plotoutline'] = video.shortDescription

    if video.longDescription:
      info_dict['plot'] = video.longDescription

    if '&' in info_dict['plot']:
      info_dict['plot'] = htmlparser.unescape(info_dict['plot'])

    if '&' in info_dict['plotoutline']:
      info_dict['plotoutline'] = htmlparser.unescape(info_dict['plotoutline'])

    # Extract airdate from title, e.g. The Project
    m = re.match(re.compile('(.+?),?\s*-?\s* (?:(?:Mon|Tues?|Wed(?:nes)?|Thu(?:rs)?|Fri|Sat(?:ur)?|Sun)(?:day)?)?\s*(\d+?)?(?:st|nd|rd|th)?\s*(?:of)?\s*(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember))\s*(\d+?)?(?:st|nd|rd|th)?(?:\s+(\d+))?', re.IGNORECASE), video.name)
    if m:
      self.log.debug('airdate matches: title=%s, showname=%s, day=%s, month=%s, day2=%s, year=%s' % (video.name, m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)))

      day = None
      month = None
      year = None
      if m.group(2) and int(m.group(2)) != 0:
        day = int(m.group(2))
      elif m.group(4) and int(m.group(4)) != 0:
        day = int(m.group(4))

      monthName = m.group(3)
      if monthName and len(monthName) != 0:
        date = None
        try:
          date = strptime(monthName,'%b')
        except ValueError:
          pass
        if date is None:
          try:
            date = strptime(monthName,'%B')
          except ValueError:
            pass
        if date:
          month = date.month

      if m.group(5) and int(m.group(5)) != 0:
        if len(m.group(5)) == 2:
          year = 2000 + int(m.group(5))
        else:
          year = int(m.group(5))

      if day is not None and month is not None:
        if year is None:
          self.log.debug('Year not specified, assuming current year')
          year = datetime.datetime.now().year
        aired = datetime.date(year, month, day).strftime('%Y-%m-%d')
        info_dict['aired'] = aired
        self.log.debug('Extracted date aired from title: %s (%s)' % (video.name, aired))

    # Extract TV Show name, Season/Episode from title
    m = re.match('(.+?)\s*-\s*S(\d+?)\s*Ep\.?\s*(\d+)', video.name)
    if m:
      regex_dict = {'tvshowtitle': m.group(1), 'season': m.group(2), 'episode': m.group(3)}
      info_dict.update(regex_dict)
      self.log.debug('Found video info from regex: %s' % repr(regex_dict))

    # Extract TV Show name, Season/Episode from custom fields
    if 'tv_show' in video.customFields:
      info_dict['tvshowtitle'] = video.customFields['tv_show']
    if 'tv_season' in video.customFields:
      info_dict['season'] = video.customFields['tv_season']
    if 'tv_episode' in video.customFields:
      m = re.match('^.+/(\d+)$', video.customFields['tv_episode'])
      if m:
        episode = int(m.group(1))
        if episode != 0:
          info_dict['episode'] = episode

    if 'cast' in video.customFields:
      info_dict['cast'] = video.customFields['cast'].split(',')
    if 'program_classification' in video.customFields:
      if 'consumer_advice' in video.customFields:
        info_dict['mpaa'] = '%s: %s' % (video.customFields['program_classification'], video.customFields['consumer_advice'])
      else:
        info_dict['mpaa'] = video.customFields['program_classification']
    if 'tv_channel' in video.customFields:
      info_dict['studio'] = video.customFields['tv_channel']
    if 'production_company_distributor' in video.customFields:
      info_dict['studio'] = video.customFields['production_company_distributor']
    if 'video_type_short_form' in video.customFields:
      if video.customFields['video_type_short_form'] == 'News clip':
        info_dict['genre'] = 'News'

    return info_dict
