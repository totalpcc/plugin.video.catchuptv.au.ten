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
import menu
import play
import playlist
import showlist
import videolist

from utils import Utils
from xbmcswift2 import Plugin

class Addon:
  def __init__(self):
    self.plugin = Plugin()
    self.plugin.register_module(menu.Module(), '')
    self.plugin.register_module(showlist.Module(), '')
    self.plugin.register_module(playlist.Module(), '')
    self.plugin.register_module(videolist.Module(), '')
    self.plugin.register_module(play.Module(), '')

    self.utils = Utils(self.plugin)
    self.utils.log_init()

  def run(self):
    try:
      self.plugin.run()
    except KeyboardInterrupt:
      pass
    except SystemExit:
      pass
    except:
      self.utils.handle_error()
