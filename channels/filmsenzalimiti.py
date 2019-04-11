# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Unicorn / XBMC Plugin
# Canale Filmsenzalimiti
# ------------------------------------------------------------

import re
import urlparse

from platformcode import config
from platformcode import logger
from core import httptools
from core import scrapertools
from core import servertools
from core import cloudflare
from core.item_ext import ItemExt as Item
from lib import unshortenit

__channel__ = "filmsenzalimiti"
host = "https://www.filmsenzalimiti.io"

headers = [['User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'],
           ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'],
           ['Accept-Encoding', 'gzip, deflate'],
           ['Referer', host],
           ['Cache-Control', 'max-age=0']
]

def mainlist(item):
    logger.info("[filmsenzalimiti] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]FILM - [COLOR orange]Al Cinema[/COLOR][/COLOR]",
                     action="peliculas",
                     url = "%s/film-del-cinema/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/popcorn_cinema_movie.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]FILM - [COLOR orange]Ultimi inseriti[/COLOR][/COLOR]",
                     action="peliculas",
                     url="%s/lastnews" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/movie_new.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]FILM - [COLOR orange]Per Genere[/COLOR][/COLOR]",
                     action="peliculas_category",
                     url=host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/movie_genre.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow][I]Cerca...[/I][/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/search.png")]

    return itemlist

# ==================================================================================================================================================

def newest(categoria):
    logger.info("[filmsenzalimiti] newest" + categoria)
    itemlist = []
    item = Item()
    try:
        if categoria == "peliculas":
            item.url = host
            item.action = "peliculas"
            item.extra = "movie"
            itemlist = peliculas(item)

            if itemlist[-1].action == "peliculas":
                itemlist.pop()

    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            logger.error("{0}".format(line))
        return []

    return itemlist

# ==================================================================================================================================================

def search(item, texto):
    logger.info("[filmsenzalimiti] " + item.url + " search " + texto)
    item.url = host + "/?do=search&mode=advanced&subaction=search&story=" + texto

    try:
        return peliculas(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ==================================================================================================================================================

def peliculas(item):
    logger.info("[filmsenzalimiti] peliculas")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    patron = r'div class="mshort".*?href="(.*?)".*?src="(.*?)".*?//.*?/(.*?)\.'
    matches = re.compile(patron, re.S).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle  in matches:
        scrapedthumbnail = host + scrapedthumbnail
        scrapedtitle = re.sub(r'([0-9])', "", scrapedtitle)
        scrapedtitle = scrapedtitle.replace("-"," ")
        scrapedtitle = scrapedtitle.replace("streaming", "")
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title="[COLOR azure]" + scrapedtitle.title() + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 fulltitle=scrapedtitle,
                 show=scrapedtitle))

    # Extrae el paginador
    patronvideos = '<a href="(.*?)">&raquo;'
    matches = re.compile(patronvideos, re.MULTILINE).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 extra="movie",
                 thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/next.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_category(item):
    logger.info("[filmsenzalimiti] peliculas_category")
    itemlist = []

    # Scarica la pagina
    data = httptools.downloadpage(item.url).data

    # Prende il blocco interessato
    blocco = r'<option value="(.*?)">(.*?)<'
    matches = re.compile(blocco, re.S).findall(data)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = scrapedurl.replace ("#", "anime/")
        scrapedurl = host + "/" + scrapedurl
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] ",
                 url=scrapedurl,
                 folder=True))
    return itemlist

# ==================================================================================================================================================

def peliculas_year(item):
    logger.info("[filmsenzalimiti] peliculas_year")
    itemlist = []

    # Scarica la pagina
    data = httptools.downloadpage(item.url).data

    # Prende il blocco interessato
    blocco = r'<ul class="anno_list">(.*?)</ul>'
    matches = re.compile(blocco, re.S).findall(data)
    for scrapedurl in matches:
        blocco = scrapedurl

    # Estrae argomenti
    patron = r'<li>.*?href="(.*?)">(.*?)</a>'
    matches = re.compile(patron, re.S).findall(blocco)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] ",
                 url=host + scrapedurl,
                 folder=True))
    return itemlist

# ==================================================================================================================================================

def peliculas_a_z(item):
    logger.info("[filmsenzalimiti] peliculas_a-z")
    itemlist = []

    # Scarica la pagina
    data = httptools.downloadpage(item.url).data

    # Prende il blocco interessato
    blocco = r'<div class="movies-letter">(.*?)<div'
    matches = re.compile(blocco, re.S).findall(data)
    for scrapedurl in matches:
        blocco = scrapedurl

    # Estrae argomenti
    patron = r'<a title="(.*?)".*?href="(.*?)"'
    matches = re.compile(patron, re.S).findall(blocco)

    for scrapedtitle, scrapedurl in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas2",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] ",
                 url=host + scrapedurl,
                 folder=True))
    return itemlist

# ==================================================================================================================================================

def findvideos(item):
    logger.info("[filmsenzalimiti] findvideos")

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    data, status = unshortenit.unshorten(data)
    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[COLOR azure][[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.show])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist