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

import os
import sys
import urlparse

try:
  import xbmcplugin
  IS_XBMC = True
except ImportError:
  IS_XBMC = False # for PC debugging

# Add our resources/lib to the python path
try:
   current_dir = os.path.dirname(os.path.abspath(__file__))
except:
   current_dir = os.getcwd()

sys.path.append(os.path.join(current_dir, 'resources', 'lib'))

import importlib
import utils

# Dynamically load module
def loadModule(moduleName):
  utils.log('Loading %s module' % moduleName)
  module = importlib.import_module('.%s' % moduleName, 'addon')
  module.Main()

# Display a XBMC error dialog
def errorDialog(err):
  if IS_XBMC:
    d = xbmcgui.Dialog()
    message = utils.dialog_error(err)
    d.ok(*message)


if ( __name__ == "__main__" ):
  utils.log('Initialised addon with arguments: %s' % repr(sys.argv))

  if ( len(sys.argv) != 3 or not sys.argv[ 2 ] ):
    loadModule('playlist')
  else:
    qs = sys.argv[ 2 ]
    if ( qs.startswith('?') ):
      qs = qs[1:]
    params = urlparse.parse_qs(qs)
    if ( 'action' in params and len(params['action']) == 1 and params['action'][0]):
      try:
        loadModule(params['action'][0])
      except:
        errorDialog('An error occured. Check the log for details.')
        utils.log_error()
    else:
      utils.log('Warning: Un-handled query string, loading playlist')
      loadModule('playlist')