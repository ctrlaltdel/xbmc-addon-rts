# vim: set fileencoding=utf-8 ts=2 expantab :
from xbmcswift2 import Plugin
import urllib
import re
from resources.lib.rts import RTS

plugin = Plugin()
rts = RTS()

def link(label, path):
  return {'label': label, 'path': plugin.url_for('category', path=path)}

@plugin.route('/')
def index():
  return [
    {'label': 'Emissions', 'path': plugin.url_for('emissions')},
    {'label': 'Info', 'path': plugin.url_for('info')},
    {'label': 'Sport', 'path': plugin.url_for('sport')},
    {'label': 'RTS +7', 'path': plugin.url_for('plus7')},
  ]

@plugin.route('/emissions/')
def emissions():
  return [
    link('Choix de la semaine', '/'),
    link('Nouvelles vidéos', '/emissions/nouvelles-videos'),
    link('Top 50', '/emissions/top'),
    {'label': 'Emissions', 'path': plugin.url_for('emissions_liste')},
  ]

@plugin.route('/emissions/liste/')
def emissions_liste():
  return [ link(title, path) for path, title in rts.get_categories('/emissions/liste') ]

@plugin.route('/info/')
def info():
  return [
    link('Info en continu', '/info'),
    link('12:45', '/info/journal-12h45'),
    link('19:30', '/info/journal-19h30'),
    link('Couleurs locales', '/info/couleurs-locales'),
    link('Top 10', '/info/top'),
  ]

@plugin.route('/sport/')
def sport():
  return [
    link('Choix de la semaine', '/sport'),
    link('Nouvelles vidéos', '/sport/nouvelles-videos'),
    link('Top 10', '/sport/top'),
    link('Emissions', '/sport/emissions-disciplines'),
  ]

@plugin.route('/plus7/')
def plus7():
  return [
    link('Nouvelles vidéos', '/plus7'),
    link('Séries', '/plus7/series'),
    link('Docs', '/plus7/docs'),
    link('Jeunesse', '/plus7/jeunesse'),
    link('Divertissement', '/plus7/divertissement'),
  ]

@plugin.route('/category/<path>/')
def category(path):
  plugin.log.debug(path)
  return [
    { 'label': title,
      'path': plugin.url_for('play', id=id),
      'is_playable': True,
      'thumbnail': thumbnail,
    } for title, id, thumbnail in rts.get_videos(path)]

@plugin.route('/play/<id>/')
def play(id):
  plugin.log.info('Playing video %s' % id)
  return plugin.play_video({'label': id, 'path': rts.get_media(id)})

if __name__ == '__main__':
  plugin.run()
