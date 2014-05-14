#!/usr/bin/env python
# vim: set fileencoding=utf-8 ts=2 expandtab :

import urllib
import urllib2
import re
import json
import os
import HTMLParser
from xml.dom import minidom

class RTS:
  BASE_URL = 'http://www.rts.ch/video'

  def __init__(self):
    self.htmlparser = HTMLParser.HTMLParser()

  def get_categories(self, path):
    PATTERN = '<a href="([^"]+)" class="video-tab-link">\s+([^<]+)</a>'

    try:
      url = self.BASE_URL + path + '/?f=video/tab'
      html = urllib.urlopen(url).read()
    except:
      raise Exception('HTTP Request failure: url=%s' % url)

    items = re.findall(PATTERN, html)

    # Remove '/video' prefix in URL
    return map(lambda x: (x[0][6:], x[1]), items)

  def get_videos(self, path):
    PATTERN = '<a.*?title="(.+?)".*?data-video-id="(.+?)".*?<img src="(.+?)"'

    try:
      url = self.BASE_URL + path + '/?f=video/tab'
      html = urllib.urlopen(url).read()
    except:
      raise Exception('HTTP Request failure: url=%s' % url)

    items = []

    try:
      for title, id, thumbnail in re.findall(PATTERN, html, re.DOTALL):
        title = self.htmlparser.unescape(title.decode('utf8'))
        thumbnail = thumbnail.split('?')[0]
        items.append((title, id, self.BASE_URL + thumbnail))
      assert len(items) > 0
    except:
      raise Exception("Regex failure: html=%s" % html)

    return items
   
  def get_media(self, id):
    # Copied from https://gist.github.com/0xced/943949
    jsonURL = "http://www.rts.ch/?format=json/video&id=%s" % id
    jsonData = urllib2.urlopen(jsonURL).read()
    result = json.loads(jsonData)
    try:
      media = sorted(result["video"]["JSONinfo"]["media"], key=lambda x: x['rate'])[-1]['url']
      baseURL = result["video"]["JSONinfo"].get("download") # was previously "http://media.tsr.ch/xobix_media/"
    except:
      raise Exception("Media not found")

    akastreamingPrefix = "http://akastreaming.tsr.ch/ch/"
    if media.startswith(akastreamingPrefix):
      mediaPath = media[len(akastreamingPrefix):]
      fileName = os.path.splitext(os.path.split(mediaPath)[1])[0] + ".flv"
      tokenURL = "http://www.rts.ch/token/ch-vod.xml?stream=media"
      try:
        dom = minidom.parse(urllib2.urlopen(tokenURL))
        #cprint(dom.toxml(), 'cyan')
      except:
        raise Exception("Could not get token")

      hostname = dom.getElementsByTagName("hostname")[0].firstChild.data
      appName = dom.getElementsByTagName("appName")[0].firstChild.data
      authParams = dom.getElementsByTagName("authParams")[0].firstChild.data

      path = 'rtmp://%s:1935 app=%s?ovpfv=2.1.7&%s playpath=mp4:media/%s swfUrl=http://www.rts.ch/swf/player.swf pageUrl=http://www.rts.ch/video/' % (hostname, appName, authParams, mediaPath)
      return path
    else:
      return result["video"]["JSONinfo"]["streams"].get("tv")

# Testing
if __name__ == '__main__':
  rts = RTS()
  print rts.get_media(4782273)
