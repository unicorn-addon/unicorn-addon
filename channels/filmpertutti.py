# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Thegroove360 - XBMC Plugin
# Canale  per filmpertutti.co
# # ------------------------------------------------------------

import re
import urlparse

from core import httptools
from platformcode import logger
from core import scrapertools
from core import servertools
from core.item_ext import ItemExt as Item
from platformcode import config

__channel__ = "filmpertutti"
__category__ = "F,S,A"
__type__ = "generic"
__title__ = "filmpertutti"
__language__ = "IT"

host = "https://www.filmpertutti.club"


def mainlist(item):
    logger.info("[thegroove360.filmpertutti] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Ultimi film inseriti[/COLOR]",
                     action="peliculas",
                     extra="movie",
                     url="%s/category/film/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Categorie film[/COLOR]",
                     action="categorias",
                     url="%s/category/film/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[/COLOR]",
                     extra="tvshow",
                     action="peliculas",
                     url="%s/category/serie-tv/" % host,
                     thumbnail="http://orig03.deviantart.net/6889/f/2014/079/7/b/movies_and_popcorn_folder_icon_by_matheusgrilo-d7ay4tw.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="tvshow",
                     thumbnail="http://dc467.4shared.com/img/fEbJqOum/s7/13feaf0c8c0/Search")]

    return itemlist


def newest(categoria):
    logger.info("[thegroove360.filmpertutti] newest" + categoria)
    itemlist = []
    item = Item()
    try:
        if categoria == "peliculas":
            item.url = host + "/category/film/"
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


def peliculas(item):
    logger.info("[thegroove360.filmpertutti] peliculas")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti
    patron = r'<li><a href=\"([^\"]+)\" data-thumbnail=\"([^\"]+)\".*?title\">(.*?)<.*?IMDb\">(.*?)<'
    matches = re.compile(patron, re.MULTILINE | re.S).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scraprate in matches:
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos" if item.extra == "movie" else "seasons",
                 contentType="movie",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] - IMDb: " + scraprate,
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra=item.extra,
                 folder=True))

    # Paginazione
    patronvideos = '<a href=\"([^\"]+)\">Pagina'
    matches = re.compile(patronvideos, re.MULTILINE).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="HomePage",
                 title="[COLOR yellow]Torna Home[/COLOR]",
                 folder=True)),
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivo >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="http://2.bp.blogspot.com/-fE9tzwmjaeQ/UcM2apxDtjI/AAAAAAAAeeg/WKSGM2TADLM/s1600/pager+old.png",
                 extra=item.extra,
                 folder=True))

    return itemlist


def categorias(item):
    logger.info("[thegroove360.filmpertutti] categorias")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    # Narrow search by selecting only the combo
    patron = '<option>Scegli per Genere</option>(.*?)</select'
    bloque = scrapertools.get_match(data, patron)

    # The categories are the options for the combo
    patron = '<option data-src="([^"]+)">([^<]+)</option>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        scrapedurl = urlparse.urljoin(item.url, scrapedurl)
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 extra=item.extra,
                 plot=scrapedplot))

    return itemlist


def search(item, texto):
    logger.info("[thegroove360.filmpertutti] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto
    try:
        return peliculas(item)
    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def seasons(item):
    data = httptools.downloadpage(item.url).data
    patron = r'<div id=\"season\">.*?<span>(.*?)</span></li></ul>(.*?)</table></div></div></div></div></div></div></div></div></div>'
    matches = re.compile(patron, re.MULTILINE | re.S).findall(data)

    itemlist = []

    for scrapedtitle, html in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 contentType="episode",
                 title="[COLOR azure]%s[/COLOR]" % scrapedtitle,
                 url=html,
                 thumbnail=item.thumbnail,
                 fulltitle=scrapedtitle + item.show,
                 show=item.show))

    return itemlist


def episodios(item):

    print item.url

    data = item.url
    patron = r'episode-wrap\">.*?season-no\">(.*?)</(.*?:;\">(.*?)</a><br>.*?)</div>'

    itemlist = []

    matches = re.compile(patron, re.MULTILINE | re.S).findall(data)

    for episode, html, title in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 contentType="episode",
                 title=episode + " - [COLOR azure]%s[/COLOR]" % title,
                 url=html,
                 extra=item.extra,
                 thumbnail=item.thumbnail,
                 fulltitle=episode + " - " + title,
                 show=item.show))

    if config.get_videolibrary_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title="Aggiungi alla libreria",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios" + "###" + item.extra,
                 show=item.show))


    return itemlist


def findvideos(item):
    def add_myitem(sitemlist, scontentType, stitle, surl):
        sitemlist.append(
            Item(channel=__channel__,
                 action="play",
                 contentType=scontentType,
                 title=stitle,
                 fulltitle=item.fulltitle,
                 server=stitle,
                 url=surl,
                 thumbnail=item.thumbnail,
                 extra=item.extra))

    logger.info("[thegroove360.filmpertutti] findvideos")
    itemlist = []
    logger.debug(item)

    # Carica la pagina
    if item.contentType == 'episode':

        regex = r'<a .*? data-link=\"([^\"]+)\"'
        fvideo = scrapertools.find_single_match(item.url, regex)
        itemlist.append(
            Item(channel=__channel__,
                 action="play",
                 contentType="episodios",
                 title="[COLOR azure]" + servertools.get_server_from_url(fvideo) + "[/COLOR]",
                 fulltitle=item.fulltitle,
                 url=fvideo,
                 thumbnail=item.thumbnail,
                 extra=item.extra))

        patron = r'<a.*?href=\"(http.*?)\">.*?>(.*?)</a>.*?<td>(.*?)<.*?<td>(.*?)<'
        matches = re.compile(patron, re.MULTILINE).findall(item.url)

        for lurl, lsrv, lqual, lang in matches:
            itemlist.append(
                Item(channel=__channel__,
                 action="play",
                 contentType="episodios",
                 title="[COLOR azure]" + lsrv + "[/COLOR] [" + lqual + "]" + " - " + lang,
                 fulltitle=item.fulltitle,
                 url=lurl,
                 thumbnail=item.thumbnail,
                 extra=item.extra))

    else:
        # Carica la pagina
        data = httptools.downloadpage(item.url).data
        patron = r'<strong>\s*(Versione.*?)<p><strong>Download'
        data = re.compile(patron, re.DOTALL).findall(data)

        if data:
            vqual = re.compile('ersione:.*?>\s*(.*?)<').findall(data[0])
            sect = re.compile('Streaming', re.DOTALL).split(data[0])

            ## SD links

            for sec in sect[1:]:
                links = re.compile('<a\s*href="([^",\s]+).*?>([^<]+)', re.DOTALL).findall(sec)
                for link, srv in links:
                    itemlist.append(
                        Item(channel=__channel__,
                             action="play",
                             contentType="movie",
                             title="[COLOR azure] " + vqual[0] + "[/COLOR] - " + srv,
                             fulltitle=item.fulltitle,
                             url=link,
                             thumbnail=item.thumbnail,
                             extra=item.extra))

        else:
            itemlist = servertools.find_video_items(item=item)

    for item in itemlist:
        logger.info(item)

    return itemlist


def play(item):
    logger.info("[thegroove360.filmpertutti] play: %s" % item.url)
    url = item.url

    from lib import unshortenit
    url, status = unshortenit.unshorten(url)

    itemlist = servertools.find_video_items(data=url)

    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(
            ['[COLOR azure][[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.show])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
