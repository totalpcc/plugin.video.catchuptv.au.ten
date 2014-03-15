#
#   Network Ten CatchUp TV Video API Library
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

# Try importing default modules, but if that doesn't work
# we might be old platforms with bundled deps
try:
  from BeautifulSoup import BeautifulSoup
except ImportError:
  from deps.BeautifulSoup import BeautifulSoup

try:
  import simplejson as json
except ImportError:
  try:
    import deps.simplejson as json
  except ImportError:
    import json

import os
import sys
import re
import urlparse
import urllib
from brightcove.api import Brightcove
from brightcove.core import get_item
from networktenvideo.objects import Show, ShowItemCollection, PlaylistItemCollection, MediaRenditionItemCollection
from networktenvideo.amf import BrightCoveAMFHelper

API_TOKEN = 'lWCaZyhokufjqe7H4TLpXwHSTnNXtqHxyMvoNOsmYA_GRaZ4zcwysw..'
PLAYER_KEY = 'AQ~~,AAACAC_zRoE~,GmfXBj8vjuSBlqMYKWGHoiljZL-ccjXh'
AMF_SEED = 'f94a0d8cf273ee668a1d9b7e6b7053148fb54065'
SWF_URL = 'http://admin.brightcove.com/viewer/us20130702.1553/connection/ExternalConnection_2.swf'
PAGE_URL = 'http://tenplay.com.au/'
FANART_BOOTSTRAP_URL = 'https://gist.github.com/adammw/8662672/raw/fanart.json'
OVERRIDES_URL = 'https://gist.github.com/adammw/8662672/raw/overrides.json'
EPISODES_URL = 'http://tenplay.com.au/Handlers/GenericUserControlRenderer.ashx?path=~/UserControls/Browse/Episodes.ascx&props=ParentID,{%s}'
SHOWDATA_URL = 'https://gist.github.com/adammw/b1ce5f1a41b9f030b824/raw/show-data.json'
MOBILEDATA_URL = 'http://tenplay.com.au/web%20api/mobilepreloaddata'
DEFAULT_SEARCH_ARGS = {
  'video_fields': 'id,name,publishedDate,shortDescription,length,videoStillURL,creationDate,lastModifiedDate',
  'custom_fields': 'start_date_au,end_date_au,start_date_nsw,end_date_nsw,start_date_act,end_date_act,start_date_vic,end_date_vic,start_date_tas,end_date_tas,start_date_sa,end_date_sa,start_date_wa,end_date_wa,start_date_nt,end_date_nt,start_date_qld,end_date_qld,start_date_au,end_date_au,prevent_sony,prevent_web,prevent_mobile_web,prevent_ios,prevent_android,prevent_xbox,prevent_windows_app,tv_channel,tv_show,tv_season,tv_episode,cast,video_type_long_form,video_type_short_form,program_classification,consumer_advice,expiry_date,expiry_tag,series_crid_id,episode_crid_id,production_company_distributor',
  'none': 'prevent_web:true',
  'get_item_count': 'true',
  'page_size': 100,
  'page_number': 0
}

class NetworkTenVideo:
  def __init__(self, caching_decorator=None):
    self.brightcove = Brightcove(API_TOKEN)
    if caching_decorator:
      self._request = caching_decorator(self._request)

    # preload data
    self.mobile_data = json.loads(self._request(MOBILEDATA_URL))
    try:
      self.fan_art_bootstarp = json.loads(self._request(FANART_BOOTSTRAP_URL))
    except Exception, e:
      pass
    try:
      self.overrides = json.loads(self._request(OVERRIDES_URL))
    except Exception, e:
      print "Could not load overrides from %s" % OVERRIDES_URL
      self.overrides = {}

  def _request(self, url, data=None):
    '''Returns a response for the given url and data.'''
    conn = urllib.urlopen(url, data)
    if conn.getcode() is not 200:
      raise Exception('Request Failure: ' + url)
    resp = conn.read()
    conn.close()
    return resp

  def get_fanart(self, show):
    # use pre-calculated from bootstrap
    if self.fan_art_bootstarp and show['ShowPageItemId'] in self.fan_art_bootstarp:
        return self.fan_art_bootstarp[show['ShowPageItemId']]

    print "Fanart Bootstrap Miss for %s with id %s" % (show['Title'], show['ShowPageItemId'])

    # educated guesses
    channel = re.sub(r'[^a-z0-9A-Z-]+','', show['Channel'].lower().replace(' ','-'))
    show_name = re.sub(r'[^a-z0-9A-Z-]+','', show['Title'].lower().replace(' ','-'))

    # try to determine correct show url
    try:
      resp = self._request(EPISODES_URL % show['ShowPageItemId'])
      episode_list_html = BeautifulSoup(resp)
      urls = episode_list_html.findAll('a', {'href': True})
      for url in urls:
        url = url['href']
        if url.startswith('/' + channel):
          show_name = url.split('/')[2]
          break
    except Exception, e:
      pass

    # find the fanart on the show url
    if len(channel) == 0 or len(show_name) == 0:
      return None
    
    # load the show url and try and find the first image that isn't a screenshot from a video
    try:
      resp = self._request('http://tenplay.com.au/' + channel + '/' + show_name)
      show_page_html = BeautifulSoup(resp)
      images = show_page_html.find('div', 'marquee-container').findAll('div', 'marquee-image')
      for image in images:
        url = image.find('div', {'data-src': True})['data-src']
        if url.startswith('//'):
          url = 'http:' + url
        if url.startswith('http://iprx.ten.com.au/ImageHandler.ashx') or len(url) == 0:
          continue
        url = url.split('?')[0]
        print "Using fanart from show page: %s" % url
        return url
    except Exception, e:
      pass

    # fallback to a screenshot from the episode listing page
    try:
      images = episode_list_html.findAll('img', {'src': True})
      for image in images:
        if len(image['src']) != 0:
          print "Using fanart from episode list: %s" % image['src']
          return image['src']
    except Exception, e:
      pass

    return None

  def get_homepage(self):
    self.mobile_data
    # TODO 

  def get_config(self):
    resp = self._request(MOBILEDATA_URL)
    json_data = json.loads(resp)
    return self.mobile_data['configuration']

  def get_news(self):
    config = self.get_config()
    news = []
    for key, value in config['brightcoveNewsQuery'].items():
      news.append({
        'Id': key,
        'Query': config['brightcoveNewsQuery'][key],
        'Title': config['brightcoveNewsQueryTitles'][key]
      })
    return news

  def get_sports(self):
    config = self.get_config()
    sports = []
    for key, value in config['brightcoveSportsQuery'].items():
      sports.append({
        'Id': key,
        'Query': config['brightcoveSportsQuery'][key],
        'Title': re.sub('([A-Z])',' \\1', key).title().strip()
      })
    return sports

  def get_shows(self):
    # load shows
    shows = self.mobile_data['shows']

    # apply overrides
    for show in shows:
      if show['ShowPageItemId'] in self.overrides:
        override = self.overrides[show['ShowPageItemId']]
        if 'ignore' in override:
          shows.remove(show)
        else:
          show.update(self.overrides[show['ShowPageItemId']])
    return shows

  def get_show(self, show):
    resp = self._request(SHOWDATA_URL)
    json_data = json.loads(resp)
    for showSearch in json_data['shows']:
      if showSearch['showName'] == show:
        return get_item(showSearch, Show)
    return None

  def get_playlists_for_show(self, show):
    resp = self._request(SHOWDATA_URL)
    json_data = json.loads(resp)
    for showSearch in json_data['shows']:
      if showSearch['showName'] == show:
        return get_item({'items': showSearch['playlists']}, PlaylistItemCollection)
    return None

  def search_videos(self, **kwargs):
    params = dict(DEFAULT_SEARCH_ARGS)
    params.update(kwargs)

    return self.brightcove.search_videos(**params)

  def get_videos_for_playlist(self, playlist, **kwargs):
    params = dict(DEFAULT_SEARCH_ARGS)
    params.update(playlist.query)
    params.update(kwargs)
    
    return self.brightcove.search_videos(**params)

  def get_media_for_video(self, videoId=None, video=None):
    # Note to self: Although we *can* access the video content via the Media API
    # (docs: http://support.brightcove.com/en/video-cloud/docs/accessing-video-content-media-api)
    # and it's much easier/flexible, we aren't so as not to arouse suspicion and to future proof the library
    #self.brightcove.find_video_by_id(video.id, fields='length,renditions,FLVURL')
    if video:
      videoId = video.id
    amfHelper = BrightCoveAMFHelper(PLAYER_KEY, videoId, PAGE_URL, AMF_SEED)
    return get_item({'items':amfHelper.data['renditions']}, MediaRenditionItemCollection)
