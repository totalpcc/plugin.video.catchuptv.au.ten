try:
  import simplejson as json
except ImportError:
  try:
    import deps.simplejson as json
  except ImportError:
    import json

import re
import config

from urllib import urlopen

class VersionCheck:
  def __init__(self, log):
    self.log = log

  def fetch_tags(self):
    return json.load(urlopen("%s/tags" % config.GITHUB_API_URL))

  def get_versions(self):
    tags = self.fetch_tags()
    self.log.debug('[VersionCheck] Found tags: %s' % tags)
    tag_names = map(lambda tag: tag['name'], tags)
    versions = filter(lambda tag: re.match(r'v(\d+)\.(\d+)(?:\.(\d+))?', tag), tag_names)
    return map(lambda tag: map(lambda v: int(v), tag[1::].split('.')), versions)

  def get_latest_version(self):
    versions = self.get_versions()
    self.log.debug('[VersionCheck] Found versions: %s' % versions)
    return sorted(versions, reverse=True)[0]

  def is_latest_version(self, current_version):
    if current_version.startswith('v'):
      current_version = current_version[1::]
    current_version = map(lambda v: int(v), current_version.split('.'))
    latest_version = self.get_latest_version()
    self.log.info('[VersionCheck] Latest version: %s, Current version: %s' % (latest_version, current_version))
    return current_version == latest_version

