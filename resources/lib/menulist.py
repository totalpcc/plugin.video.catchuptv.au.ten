import sys
import os
import xbmcgui
import xbmcplugin

class Main:
    def __init__( self ):
        buttons = ( 
                ( "2010 Videos", "%s?menuId=%s" % ( sys.argv[ 0 ], "cb519624-44a2-4bf7-808b-3514d34e96e4", ),    ),
                ( "7PM Project", "%s?menuId=%s" % ( sys.argv[ 0 ], "7a6ab1fe-cd90-4143-bf79-ba376a096b2e", ),    ),
                ( "MasterChef", "%s?menuId=%s" % ( sys.argv[ 0 ], "f8066236-e138-457a-95f4-298ed80718f8", ),    ),
                ( "Neighbours", "%s?menuId=%s" % ( sys.argv[ 0 ], "ac9e06cb-4a1f-4eb0-b20f-c2f3429294b8", ),    ),
                ( "Ready Steady Cook", "%s?menuId=%s" % ( sys.argv[ 0 ], "c58a5afc-f01f-419e-a659-f2f9600b6075", ),    ),
                ( "The Biggest Loser", "%s?menuId=%s" % ( sys.argv[ 0 ], "353acb23-79a8-4eab-a080-220869355e1e", ),    ),
            )
        for button in buttons:
            xbmcplugin.addDirectoryItem(handle=int( sys.argv[ 1 ] ),listitem=xbmcgui.ListItem(button[0]),url=button[1],totalItems=len( buttons ),isFolder=True)
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=1 )