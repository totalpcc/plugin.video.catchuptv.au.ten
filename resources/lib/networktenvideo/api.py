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
  from BeautifulSoup import BeautifulStoneSoup
except ImportError:
  from deps.BeautifulSoup import BeautifulStoneSoup

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
from networktenvideo.objects import ShowItemCollection, PlaylistItemCollection, MediaRenditionItemCollection
from networktenvideo.amf import BrightCoveAMFHelper
from networktenvideo.cache import Cache

API_TOKEN = 'lWCaZyhokufjqe7H4TLpXwHSTnNXtqHxyMvoNOsmYA_GRaZ4zcwysw..'
PLAYER_KEY = 'AQ~~,AAACAC_zRoE~,GmfXBj8vjuSBlqMYKWGHoiljZL-ccjXh'
AMF_SEED = 'f94a0d8cf273ee668a1d9b7e6b7053148fb54065'
SWF_URL = 'http://admin.brightcove.com/viewer/us20130702.1553/connection/ExternalConnection_2.swf'
PAGE_URL = 'http://ten.com.au/watch-tv-episodes-online.htm'
SHOWDATA_URL = 'https://gist.github.com/adammw/5920487/raw/show-data.json'
USE_SCRAPER = False
SHOWLIST_URL = 'http://ten.com.au/NWT_showlist.js'
SHOWLIST_REGEX = re.compile('var tenShows=({.+})', re.DOTALL)
PLAYLIST_REGEX = re.compile('(?:(?<!Watch) Full Episodes|Extras)', re.IGNORECASE)
DEFAULT_SEARCH_ARGS = {
  'video_fields': 'id,name,publishedDate,shortDescription,length,videoStillURL,creationDate,lastModifiedDate',
  'custom_fields': 'start_date_au,end_date_au,start_date_nsw,end_date_nsw,start_date_act,end_date_act,start_date_vic,end_date_vic,start_date_tas,end_date_tas,start_date_sa,end_date_sa,start_date_wa,end_date_wa,start_date_nt,end_date_nt,start_date_qld,end_date_qld,start_date_au,end_date_au,prevent_sony,prevent_web,prevent_mobile_web,prevent_ios,prevent_android,prevent_xbox,prevent_windows_app,tv_channel,tv_show,tv_season,tv_episode,cast,video_type_long_form,video_type_short_form,program_classification,consumer_advice,expiry_date,expiry_tag,series_crid_id,episode_crid_id,production_company_distributor',
  'none': 'prevent_web:true',
  'get_item_count': 'true',
  'page_size': 100,
  'page_number': 0
}

if hasattr(sys.modules["__main__"], "cache"):
  cache = sys.modules["__main__"].cache
else:
  cache = Cache("networktenvideo", 24)

class NetworkTenVideo:
  def __init__(self):
    self.brightcove = Brightcove(API_TOKEN)

  def _request(self, url, data=None):
    '''Returns a response for the given url and data.'''
    conn = urllib.urlopen(url, data)
    resp = conn.read()
    conn.close()
    return resp

  if USE_SCRAPER:

    def get_shows(self):
      '''Returns a ShowItemCollection of Show results.''' 
      js = cache.cacheFunction(self._request, SHOWLIST_URL)
      json_data = re.search(SHOWLIST_REGEX, js).group(1)
      shows = json.loads(json_data)
      return get_item({'items':shows['shows']}, ShowItemCollection)

    def get_playlists_for_show(self, show):
      resp = cache.cacheFunction(self._request, show.videoLink)
      html = BeautifulStoneSoup(resp)

      # search through each show list for the box containing playlists for this show
      show_list_boxes = html.findAll('div', attrs={'class': re.compile('VL05s')})
      for div in show_list_boxes:
        header = div.find('h3', attrs={'class': re.compile('header')})
        if re.search(PLAYLIST_REGEX, header.span.string) is not None:
          tabs = div.find('ul', attrs={'class': re.compile('show-list')}).findAll('a')
          playlists = []
          for tab in tabs:
            playlists.append({'name': tab.string, 'query': urlparse.parse_qs(tab['tab-href'])})
          return get_item({'items': playlists}, PlaylistItemCollection)

      # if that didn't work, try to find the searchTagValue
      scripts = html.findAll('script')
      for script in scripts:
        if script.string:
          m = re.search(re.compile('loadVideoPage\({.*searchTagValue\s*:\s*"(.+?)".*}\)', re.DOTALL), script.string)
          if m is not None:
            return get_item({'items': {'name':'Full Episodes', 'query': m.group(1).replace(';','')}}, PlaylistItemCollection)

      return None

  else:

    def get_shows(self):
      resp = cache.cacheFunction(self._request, SHOWDATA_URL)
      json_data = json.loads(resp)
      return get_item({'items': json_data['shows']}, ShowItemCollection)

    def get_playlists_for_show(self, show):
      resp = cache.cacheFunction(self._request, SHOWDATA_URL)
      json_data = json.loads(resp)
      for showSearch in json_data['shows']:
        if showSearch['showName'] == show.showName:
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
