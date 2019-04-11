# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Unicorn - XBMC Plugin
# Canale  per eurostreaming.tv
# ------------------------------------------------------------

import re
import urlparse

from core import httptools
from core import scrapertools
from core import servertools
from core.item_ext import ItemExt as Item
from platformcode import config
from platformcode import logger
from lib import unshortenit
from core import cloudflare

__channel__ = "eurostreaming"
host = "https://eurostreaming.cafe"
headers = [['Referer', host]]

def mainlist(item):
    logger.info("[eurostreaming] mainlist")
    itemlist = [
        Item(channel=__channel__,
            title="[COLOR azure]Ultimi Aggiornamenti[/COLOR]",
            action="serietv",
            extra='tvshow',
            url=host,
            thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/serie_new.png"),
        Item(channel=__channel__,
            title="[COLOR azure]Serie TV[/COLOR]",
            action="serietv",
            extra='tvshow',
            url="%s/category/serie-tv-archive/" % host,
            thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/serie.png"),
        Item(channel=__channel__,
            title="[COLOR azure]Anime / Cartoni[/COLOR]",
            action="serietv",
            extra='tvshow',
            url="%s/category/anime-cartoni-animati/" % host,
            thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/anime.png"),
        Item(channel=__channel__,
            title="[COLOR yellow]Cerca...[/COLOR]",
            action="search",
            extra='tvshow',
            thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/search.png")]
    return itemlist

# ====================================================================================================================================================================

def serietv(item):
    logger.info("[eurostreaming] peliculas")
    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti
    patron = r'<div class="post-thumb">\s*<a href="([^"]+)" title="([^"]+)">\s*<img src="([^"]+)"'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedtitle, scrapedthumbnail in matches:
        scrapedplot = ""
        #scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle.replace("Streaming", ""))
        #if scrapedtitle.startswith("Link to "):
            #scrapedtitle = scrapedtitle[8:]
        #num = scrapertools.find_single_match(scrapedurl, '(-\d+/)')
        #if num:
            #scrapedurl = scrapedurl.replace(num, "-episodi/")
        itemlist.append(

            Item(
                channel=__channel__,
                action="season",
                fulltitle=scrapedtitle,
                show=scrapedtitle,
                title=scrapedtitle,
                url=scrapedurl,
                thumbnail=scrapedthumbnail,
                plot=scrapedplot,
                extra=item.extra,
                folder=True))

    # Paginazione
    patronvideos = '<a class="next page-numbers" href="?([^>"]+)">Avanti &raquo;</a>'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(
                channel=__channel__,
                action="HomePage",
                title="[COLOR yellow]Torna Home[/COLOR]",
                folder=True)),
        itemlist.append(
            Item(
                channel=__channel__,
                action="serietv",
                title="[COLOR orange]Successivo >>[/COLOR]",
                url=scrapedurl,
                thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/next.png",
                extra=item.extra,
                folder=True))

    return itemlist

# ====================================================================================================================================================================

def search(item, texto):
    logger.info("[eurostreaming].py] " + item.url + " search " + texto)
    item.url = "%s/?s=%s" % (host, texto)
    try:
        return serietv(item)
    # Continua la ricerca in caso di errore
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []

# ====================================================================================================================================================================

def season(item):
    logger.info("[eurostreaming] season")

    itemlist = []

    # Carica la pagina
    data = httptools.downloadpage(item.url).data

    # Estrae il contenuto
    patron = r'nano_cp_button".*?>>>.(.*?).<<<'
    matches = re.compile(patron, re.S).findall(data)

    try:
        if matches[0] == "CLICCA QUI PER APRIRE GLI EPISODI":

            # Estrae il contenuto
            patron = r'"go_to":"(.*?)"'
            matches = re.compile(patron, re.DOTALL).findall(data)
            url = matches[0]
            url = url.replace ("\\","")

            # Carica la pagina
            data = httptools.downloadpage(url).data

            # Estrae il contenuto
            patron = r'"su-spoiler-icon">.*?>(.*?)<(.*?)</div></div>'
            matches = re.compile(patron, re.S).findall(data)

            for scrapedtitle, scrapedurl in matches:
                itemlist.append(
                    Item(channel=__channel__,
                        action="episodios",
                        fulltitle=scrapedtitle,
                        show=scrapedtitle,
                        title=scrapedtitle,
                        url=scrapedurl,
                        thumbnail=item.thumbnail,
                        extra=item.extra,
                        folder=True))

            return itemlist

    except:
        # Carica la pagina
        data = httptools.downloadpage(item.url).data

        # Estrae il contenuto
        patron = r'"su-spoiler-icon">.*?>(.*?)<(.*?)</div></div>'
        matches = re.compile(patron, re.S).findall(data)

        for scrapedtitle, scrapedurl in matches:
            itemlist.append(
                Item(channel=__channel__,
                     action="episodios",
                     fulltitle=scrapedtitle,
                     show=scrapedtitle,
                     title=scrapedtitle,
                     url=scrapedurl,
                     thumbnail=item.thumbnail,
                     extra=item.extra,
                     folder=True))

        return itemlist

# ====================================================================================================================================================================

def episodios(item):
    logger.info("[eurostreaming] episodios")

    itemlist = []

    # Carica la pagina
    data = item.url

    # Estrae il contenuto
    patron = r'(.*?)<a(.*?)</a><'
    matches = re.compile(patron, re.MULTILINE).findall(data)

    for scrapedtitle, scrapedurl in matches:
        scrapedtitle = scrapedtitle.replace (" – ", "")
        scrapedtitle = scrapedtitle.replace("–", "")
        scrapedtitle = scrapedtitle.replace("<strong>", "")
        scrapedtitle = scrapedtitle.replace("</strong>", "")
        itemlist.append(
            Item(channel=__channel__,
                action="findvideos",
                fulltitle=scrapedtitle,
                show=scrapedtitle,
                title=scrapedtitle,
                url=scrapedurl,
                thumbnail=item.thumbnail,
                extra=item.extra,
                folder=True))

    return itemlist

# ====================================================================================================================================================================

def findvideos(item):
    logger.info("[eurostreaming] findvideos")

    itemlist = []

    # Descarga la pagina
    data = item.url

    patron = r'href="(.*?)".*?>([a-z0-9A-Z]+)'
    matches = re.compile(patron, re.S).findall(data)

    for scrapedurl, server in matches:
        #server = server.replace ("</a>", "")
        itemlist.append(
            Item(channel=__channel__,
                action="play",
                fulltitle="[COLOR azure][COLOR orange][" + server + "][/COLOR] - " + item.title +"[/COLOR]" ,
                show="[COLOR azure][COLOR orange][" + server + "][/COLOR] - " + item.title +"[/COLOR]",
                title="[COLOR azure][COLOR orange][" + server + "][/COLOR] - " + item.title +"[/COLOR]",
                url=scrapedurl,
                thumbnail=item.thumbnail,
                extra=item.extra,
                folder=True))

    return itemlist

# ====================================================================================================================================================================

def play(item):
    logger.info("[eurostreaming] play")

    # Descarga la pagina
    data = item.url

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