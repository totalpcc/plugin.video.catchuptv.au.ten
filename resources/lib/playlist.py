import sys
import re
import xbmcgui
import xbmcplugin
import urllib
import xml.etree.ElementTree
import time
import urllib2
import htmlentitydefs

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)
    
class Main:
    BASE_CURRENT_URL = "http://publish.flashapi.vx.roo.com/PlaylistInfoService.asmx"
    BITRATE = 700
    SOAP_XML = '<?xml version="1.0" encoding="utf-8"?><SOAP-ENV:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-ENV:Body><GetPlaylistXMLGeo xmlns="http://tempuri.org/"><SiteIdGuid>%s</SiteIdGuid><Channel>%s</Channel><Bitrate>%s</Bitrate><Format>flash</Format><ThumbnailTypeCode>square_small</ThumbnailTypeCode><RowCount>50</RowCount><StartPosition>0</StartPosition><ClipId></ClipId><Artist></Artist><Album></Album><Criteria></Criteria><RelatedLinksKeyName>ALL</RelatedLinksKeyName><GeoCountry>AUSTRALIA</GeoCountry><GeoRegion>VICTORIA</GeoRegion><GeoCity>MELBOURNE</GeoCity><GeoTimeZone>+10:00</GeoTimeZone></GetPlaylistXMLGeo></SOAP-ENV:Body></SOAP-ENV:Envelope>'
    def __init__( self ):
        params = self._parse_argv()
        data = self.SOAP_XML % (params["menuId"],params["playlistId"],self.BITRATE)
        playlistUrl = self.BASE_CURRENT_URL
        playlistReq = urllib2.Request(playlistUrl,data,{"Content-Type": "text/xml"})
        response = urllib2.urlopen(playlistReq)
        xmlStr = response.read()
        m = re.search(u'(&lt;\?xml.+?)</GetPlaylistXMLGeoResult>',xmlStr,re.DOTALL)
        if len(m.group(1)) == 0: raise
        playlistXml = unescape(m.group(1).decode('utf-8'))
        print playlistXml.encode('utf-8')
        playlist = xml.etree.ElementTree.fromstring(playlistXml.encode('utf-8'))
        videos = playlist.findall("PlaylistItem")
        episodes = dict()
        for video in videos: 
            # Part detection method 1
            # Look for (1/6) at END of title
            m = re.search('^(.+?)\(([0-9]+?)\/([0-9]+?)\)$',video.findtext("Name"))
            if (m != None):
                title = m.group(1)
                description = video.findtext("Description")
                part = m.group(2)
                totalParts = m.group(3)
            # Part detection method 2
            # Look for (1/6) at START of description
            else:
                m = re.search('^\(([0-9]+?)\/([0-9]+?)\)(.*)$',video.findtext("Description"))
                if (m != None):
                    title = video.findtext("Name")
                    description = m.group(3)
                    part = m.group(1)
                    totalParts = m.group(2)
                else:
                    # Part detection method 3
                    # Look for "Part 2" or "seg 2" in title
                    m = re.search('^(.*?)(?:\s*-\s*)?(?:[pP]art|seg)\s+?([0-9]+)(.*?)$',video.findtext("Name"))
                    if (m != None):
                        title = m.group(1) + " " + m.group(3)
                        description = video.findtext("Description")
                        part = m.group(2)
                    # Give up detecting parts, assume only 1
                    else:
                        title = video.findtext("Name")
                        description = video.findtext("Description")
                        part = 1
                        totalParts = 1
            
            if not episodes.has_key(title):
                episodes[title] = dict()
                episodes[title]["url"] = "stack://"
            episodes[title]["title"] = title
            episodes[title]["description"] = description
            episodes[title]["lastPart"] = part
            episodes[title]["totalParts"] = totalParts
            episodes[title]["url"] += video.findtext("StreamUrl") + " , "
            
            if not episodes[title].has_key("thumbnail"):
                for img in video.findall("Thumbnails/Thumbnail"):
                    if (img.get("type") == "wide_large" and len(img.text)>0):
                        episodes[title]["thumbnail"] = img.text
                        break
            if not episodes[title].has_key("date"):
                episodes[title]["date"] = time.strptime(video.findtext("Date"),"%a, %d %b %Y %H:%M:%S %Z")
        
        for key in episodes:
            episode = episodes[key]
            listItm = xbmcgui.ListItem(episode["title"])
            if episode.has_key("thumbnail") and len(episode["thumbnail"])>0:
                listItm.setThumbnailImage(episode["thumbnail"])
            
            try:
                listItm.setInfo("video",{'date': time.strftime("%d.%m.%Y",episode["date"]),'year':int(time.strftime("%Y",episode["date"])),'plot':episode["description"]})
            except: pass
            xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),
                listitem=listItm,
                url=episode["url"][0:-3],  # removes the last comma from the stack url
                totalItems=len(episodes))
            print "Adding url " + episode["url"][0:-3]
        #xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=xbmcgui.ListItem(menu.findtext("title")),url=sys.argv[ 0 ])
        #xbmcplugin.addSortMethod( handle=int(sys.argv[1], sortMethod=xbmcplugin.SORT_METHOD_DATE))
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=1 )
        
    def _parse_argv( self ):
        # parse sys.argv for params and return result
        params = dict( urllib.unquote_plus( arg ).split( "=" ) for arg in sys.argv[ 2 ][ 1 : ].split( "&" ) )
        # we need to do this as quote_plus and unicode do not work well together
        #params[ "category" ] = eval( params[ "category" ] )
        params["playlistId"] = urllib.unquote_plus(params["playlistId"])
        # return params
        return params
        
    def _fetch_url( self, url ):
        sock = urllib.urlopen(url)
        data = sock.read()
        sock.close()
        return data