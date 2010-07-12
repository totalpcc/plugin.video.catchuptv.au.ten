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
        for video in videos: 
            # Name
            listItm = xbmcgui.ListItem(video.findtext("Name"))
            
            # Thumbnail
            for img in video.findall("Thumbnails/Thumbnail"):
                if (img.get("type") == "wide_large" and len(img.text)>0):
                    listItm.setThumbnailImage(img.text)
            
            # Broadcast Date
            date = time.strptime(video.findtext("Date"),"%a, %d %b %Y %H:%M:%S %Z")
            
            try:
                listItm.setInfo("video",{'date': time.strftime("%d.%m.%Y",date),'year':int(time.strftime("%Y",date)),'plot':video.findtext("Description")})
            except: pass
            xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),
                listitem=listItm,
                url=video.findtext("StreamUrl"),
                totalItems=len(videos))
        #xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=xbmcgui.ListItem(menu.findtext("title")),url=sys.argv[ 0 ])
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