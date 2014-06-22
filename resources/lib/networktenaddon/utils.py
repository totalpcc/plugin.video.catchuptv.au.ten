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
from issue_reporter import IssueReporter
from version_check import VersionCheck
from xbmcswift2 import xbmcgui, xbmcplugin

class Utils:
  def __init__(self, plugin):
    self.plugin = plugin
    self.log = plugin.log
    self.name = plugin.name
    self.id = plugin.addon.getAddonInfo('id')
    self.version = plugin.addon.getAddonInfo('version')

  def log_init(self):
    self.log.debug('Initialising %s addon, v%s' % (self.name, self.version))

  def handle_error(self, err=""):
    traceback_str = traceback.format_exc()
    self.log.error(traceback_str)
    report_issue = False
    version_checker = VersionCheck(self.log)
    d = xbmcgui.Dialog()
    if d:
      message = self.dialog_error_msg(err)
      if version_checker.is_latest_version(self.version):
        try:
          message.append("Would you like to report this issue to GitHub?")
          report_issue = d.yesno(*message)
        except:
          message.append("If this error continues to occur, please report it on GitHub.")
          d.ok(*message)
      else:
        message.append("Please try updating this addon before reporting this issue.")
        d.ok(*message)
    if report_issue:
      self.log.debug("Reporting issue to GitHub")
      reporter = IssueReporter(self)
      issue_url = reporter.report_issue(traceback_str)
      if issue_url:
        d.ok("%s v%s Error" % (self.name, self.version), "Success. Issue reported at %s" % issue_url)

  def dialog_error_msg(self, msg=""):
    # Generate a list of lines for use in XBMC dialog
    content = []
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if (msg):
      msg = " - %s" % msg
    content.append("%s v%s Error" % (self.name, self.version))
    content.append(str(exc_value))
    content.append("[%s (%d)%s]" % (exc_traceback.tb_frame.f_code.co_name, exc_traceback.tb_lineno, msg))
    return content
