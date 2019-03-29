# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Unicorn - XBMC Plugin
# Canale per Dexter Channel
# ------------------------------------------------------------

import re

from core import httptools
from platformcode import logger
from core import scrapertools
from core import servertools
from core.item import Item

__channel__ = "dexterchannel"


def mainlist(item):
    logger.info("[dexterchannel] mainlist")

    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Dexter Channel - [/COLOR][COLOR orange]I Film[/COLOR]",
                     action="lista",
                     url="https://raw.githubusercontent.com/32Dexter/DexterRepo/master/Dexter%20Channel/Dexter%20Channel.txt",
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/popcorn_cinema_movie.png",
                     fanart="https://raw.githubusercontent.com/32Dexter/DexterRepo/master/Dexter%20Channel/dexter_wallpaper.jpg")]

    return itemlist


def lista(item):
    logger.info("[dexterchannel] lista")

    itemlist = []

    # Scarica la pagina
    data = httptools.downloadpage(item.url).data

    # Estrae i contenuti
    matches = re.compile('<div>(.*?)</div>', re.MULTILINE | re.S).findall(data)

    for match in matches:
        scrapedtitle = scrapertools.find_single_match(match, '<h1>([^<]+)</h1>')
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedthumbnail = scrapertools.find_single_match(match, '<img src=\"([^\"]+)\"')
        scrapedurl = scrapertools.find_single_match(match, '<p>(.*?)</p>')
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 title=scrapedtitle,
                 thumbnail=scrapedthumbnail,
                 url=scrapedurl))

    return itemlist


def findvideos(item):
    logger.info("[dexterchannel] findvideos")

    # Downloads page
    data = item.url

    itemlist = servertools.find_video_items(data=data)
    for videoitem in itemlist:
        videoitem.title = item.title + "[COLOR orange] - " + videoitem.title + "[/COLOR]"
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist
