import sys
import re
import xbmcgui
import xbmcplugin
import urllib
import xml.etree.ElementTree

class Main:
    BASE_CURRENT_URL = "http://publish.flashapi.vx.roo.com/xmlgenerators/menu/%s/flashmenugenerator.aspx?siteId=%s"
    def __init__( self ):
        params = self._parse_argv()
        if params["menuId"] == "default":
            params["menuId"] = "cb519624-44a2-4bf7-808b-3514d34e96e4";
        menuUrl = self.BASE_CURRENT_URL % (params["menuId"],params["menuId"])
        menu = xml.etree.ElementTree.parse(menuUrl)
        if params.has_key("nodeId"):
            for node in list(menu.getiterator("node")):
                if node.get("id") == params["nodeId"]:
                    menus = node.findall("node")
                    break
        else:
            menus = menu.findall("node")
        for node in menus: #find all submenus, as we assume that everything is two levels deep
            if len(node.getchildren()) > 0:
                xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=xbmcgui.ListItem(node.get("label")),url="%s?menuId=%s&nodeId=%s" % ( sys.argv[ 0 ], params["menuId"], node.get("id"), ),isFolder=True, totalItems=len(menus))   
            else:
                xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=xbmcgui.ListItem(node.get("label")),url="%s?playlistId=%s&menuId=%s" % ( sys.argv[ 0 ], urllib.quote_plus(node.get("command")), params["menuId"], ),isFolder=True, totalItems=len(menus))   
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=1 )
        
    def _parse_argv( self ):
        try:
            # parse sys.argv for params and return result
            params = dict( urllib.unquote_plus( arg ).split( "=" ) for arg in sys.argv[ 2 ][ 1 : ].split( "&" ) )
            # we need to do this as quote_plus and unicode do not work well together
            #params[ "category" ] = eval( params[ "category" ] )
        except:
            # no params passed
            params = { "menuId": "default"}#"category": None }
        # return params
        return params
        
    def _fetch_url( self, url ):
        sock = urllib.urlopen(url)
        data = sock.read()
        sock.close()
        return data