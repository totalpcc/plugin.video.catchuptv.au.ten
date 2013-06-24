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
#   This file includes portions from xbmc-addon-abc-iview
#   Copyright (C) 2012 Andy Botting
#

import sys
import traceback
import logging
import config

def log(s):
  print "[%s v%s] %s" % (config.NAME, config.VERSION, s)

def log_error(message=None):
  exc_type, exc_value, exc_traceback = sys.exc_info()
  if message:
    exc_value = message
  print "[%s v%s] ERROR: %s (%d) - %s" % (config.NAME, config.VERSION, exc_traceback.tb_frame.f_code.co_name, exc_traceback.tb_lineno, exc_value)
  print traceback.print_exc()

def dialog_error(msg=""):
  # Generate a list of lines for use in XBMC dialog
  content = []
  exc_type, exc_value, exc_traceback = sys.exc_info()
  if (msg):
    msg = " - %s" % msg
  content.append("%s v%s Error" % (config.NAME, config.VERSION))
  content.append("%s (%d)%s" % (exc_traceback.tb_frame.f_code.co_name, exc_traceback.tb_lineno, msg))
  content.append(str(exc_value))
  content.append("If this error continues to occur, please report it.")
  return content

def handle_logger(logger):
  class LoggingHandler(logging.Handler):
    def __init__(self, strm=None):
        logging.Handler.__init__(self)
        self.stream = sys.stdout

    def flush(self):
        pass

    def emit(self, record):
        try:
            msg = self.format(record)
            self.stream.write("%s\n" % msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

  ch = LoggingHandler()
  format = "[%s v%s] %s" % (config.NAME, config.VERSION, '[%(module)s:%(funcName)s():%(lineno)d] %(levelname)s: %(message)s')
  formatter = logging.Formatter(format)
  ch.setFormatter(formatter)
  logger.addHandler(ch)
  logger.setLevel(logging.DEBUG)
