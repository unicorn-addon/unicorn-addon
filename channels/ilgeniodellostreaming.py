# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# TheGroove360 / XBMC Plugin
# Canale per ilgeniodellostreaming
# ------------------------------------------------------------

import re
import urlparse

from platformcode import config
from platformcode import logger
from core import httptools
from core import scrapertools
from core import servertools
from core.item import Item
from core import cloudflare

__channel__ = "ilgeniodellostreaming"
host = "https://ilgeniodellostreaming.black"

headers = [
    ['User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0'],
    ['Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Referer', host],
    ['Cache-Control', 'max-age=0']
]

wait_time = (10)


# ==================================================================================================================================================

def mainlist(item):
    logger.info("[ilgeniodellostreaming] mainlist")
    itemlist = [Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Novita[/COLOR]",
                     action="peliculas",
                     url="%s/category/film/" % host,
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/movie_new.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Archivio A-Z[/COLOR]",
                     action="peliculas_az",
                     url="%s/film-a-z/" % host,
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/a-z.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Categorie[/COLOR]",
                     action="categorias",
                     url=host,
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/movie_genre.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Archivio[/COLOR]",
                     action="peliculas_tv",
                     url="%s/category/serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/serie.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Aggiornate[/COLOR]",
                     action="peliculas_tvnew",
                     url="%s/aggiornamenti-serie-tv/" % host,
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/serie_new.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime[COLOR orange] - Novita[/COLOR]",
                     action="peliculas",
                     url="%s/category/film/animazione/" % host,
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/anime.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca...[/COLOR]",
                     action="search",
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/search.png"),
                Item(channel=__channel__,
                     title="[COLOR yellow]Cerca Serie TV...[/COLOR]",
                     action="search",
                     extra="tvshow",
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/search.png")
                ]

    return itemlist


# ==================================================================================================================================================

def categorias(item):
    logger.info("[ilgeniodellostreaming] categorias")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    bloque = scrapertools.get_match(data, '<h2>Genere</h2>(.*?)</ul></div>')

    # Extrae las entradas (carpetas)
    patron = '<li class="cat-item.*?href="(.*?)">.(.*?) <'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/stesev1/channels/master/images/channels_icon/genre_P.png",
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def search(item, texto):
    logger.info("[ilgeniodellostreaming] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto

    try:
        return peliculas_search(item)

    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)

    return []


# ==================================================================================================================================================

def peliculas_search(item):
    logger.info("[ilgeniodellostreaming] peliculas_search")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = r'thumbnail animation-2.*?<a href="(.*?)".*?src="(.*?)".*?tvshows">(.*?)<.*?href.*?>(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, genere, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos" if not "tvshow" in item.extra else "episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    return itemlist

# ==================================================================================================================================================
def peliculas(item):
    logger.info("[ilgeniodellostreaming] peliculas")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron =r'<article class="item movies">.*?<a href="(.*?)".*?img src="(.*?)".*?h3.*?">(.*?)<.*?texto">(.*?)</p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    #for genre, scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
        scrapedtitle = scrapedtitle.replace("&#8217;", "")
        scrapedtitle = scrapedtitle.replace("#038;", " ")
        scrapedtitle = scrapedtitle.replace(":", " - ")
        scrapedtitle = scrapedtitle.replace("&", " e")
        scrapedtitle = scrapedtitle.replace("e#8211;", " - ")
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedplot = scrapedplot.replace("<span>", "")
        scrapedplot = scrapedplot.replace("</span>", "")
        scrapedplot = scrapedplot.replace("<p>", "")
        scrapedplot = scrapedplot.replace("&#8217;", "'")
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patronvideos = 'rel="next" href="(.*?)"'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/next.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_az(item):
    logger.info("[ilgeniodellostreaming] peliculas_az")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = r'<td class=\"mlnh-thumb\">\s<a href=\"(.*?)\".*?<img src=\"([^\"]+)\".*?<a.*?>(.*?)</a>'
    matches = re.compile(patron, re.S).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        scrapedplot = ""
        #scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        #scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] ",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patronvideos = 'rel="next".*?"(.*?)"'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_az",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/next.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_tv(item):
    logger.info("[ilgeniodellostreaming] peliculas_tv")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = r'<div class="poster"><a href="(.*?)">.*?src="(.*?)".*?h3>.*?>(.*?)<.*?<div class="texto"><p>(.*?)</p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedplot = scrapedplot.replace("<span>", "")
        scrapedplot = scrapedplot.replace("</span>", "")
        scrapedplot = scrapedplot.replace("<p>", "")
        scrapedplot = scrapedplot.replace("&#8217;", "'")
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patronvideos = 'rel="next" href="(.*?)"'
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_tv",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/next.png",
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def peliculas_tvnew(item):
    logger.info("[ilgeniodellostreaming] peliculas_tvnew")
    itemlist = []
    PERPAGE = 14

    p = 1
    if '{}' in item.url:
        item.url, p = item.url.split('{}')
        p = int(p)

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas (carpetas)
    patron = r'<div class="poster"> <img src="(.*?)".*?<a href="(.*?)".*?n; ">(.*?)<.*?"serie">(.*?)<'

    matches = re.compile(patron, re.DOTALL).findall(data)

    for i, (scrapedthumbnail, scrapedurl, scrapedtitle, episodio) in enumerate(matches):
        if (p - 1) * PERPAGE > i: continue
        if i >= p * PERPAGE: break
        scrapedplot = ""
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        scrapedtitle = scrapedtitle+ " " + episodio
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios_new",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    if len(matches) >= p * PERPAGE:
        scrapedurl = item.url + '{}' + str(p + 1)
        itemlist.append(
            Item(channel=__channel__,
                 extra=item.extra,
                 action="peliculas_tvnew",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/next.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def episodios(item):
    logger.info("[ilgeniodellostreaming] episodios")
    itemlist = []

    data = scrapertools.cache_page(item.url)

    patron = r'data-darkreader-inline-color="">.*?>(.*?)<.*?(<p>.*?)<p>'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="episodios_list",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR orange]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))

    return itemlist

## ==================================================================================================================================================

def episodios_list(item):
    logger.info("[ilgeniodellostreaming] episodios")
    itemlist = []

    data = item.url

    patron = r'>(.*?)<a(.*?)<br /'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedtitle, scrapedurl in matches:
        scrapedtitle = scrapedtitle.replace ("-", "")
        scrapedtitle = scrapedtitle.replace ("&#8211;", "")
        scrapedtitle = scrapedtitle.replace (" 1", "1")
        scrapedtitle = scrapedtitle.replace (" 2", "2")
        scrapedtitle = scrapedtitle.replace (" 3", "3")
        scrapedtitle = scrapedtitle.replace (" 4", "4")
        scrapedtitle = scrapedtitle.replace (" 5", "5")
        scrapedtitle = scrapedtitle.replace (" 6", "6")
        scrapedtitle = scrapedtitle.replace (" 7", "7")
        scrapedtitle = scrapedtitle.replace (" 8", "8")
        scrapedtitle = scrapedtitle.replace (" 9", "9")
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR orange]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def episodios_new(item):
    logger.info("[ilgeniodellostreaming] categorias")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    bloque = scrapertools.get_match(data, '</script></div><div class="sbox"><h2>(.*?)</div></div><script>')

    # Extrae las entradas (carpetas)
    patron = '<img src="([^"]+)"><\/a><\/div><div\s*class="numerando">([^<]+)<\/div>'
    patron += '<div class[^>]+><a\s*href="([^"]+)">([^<]+)<\/a>'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapededthumbnail, scrapedep, scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=item.fulltitle + " -" + scrapedep + " " + scrapedtitle,
                 show=item.show + " -" + scrapedep + " " + scrapedtitle,
                 title="[COLOR azure]" + scrapedep + "  [COLOR orange]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot="[COLOR orange]" + item.fulltitle + "[/COLOR] " + item.plot,
                 folder=True))

    if config.get_library_support() and len(itemlist) != 0:
        itemlist.append(
            Item(channel=__channel__,
                 title=item.title + " [COLOR yellow] Aggiungi alla libreria [/COLOR]",
                 url=item.url,
                 action="add_serie_to_library",
                 extra="episodios",
                 show=item.show))
        itemlist.append(
            Item(channel=item.channel,
                 title="Scarica tutti gli episodi della serie",
                 url=item.url,
                 action="download_all_episodes",
                 extra="episodios",
                 show=item.show))

    return itemlist


# ==================================================================================================================================================

'''
def findvideos(item):
    logger.info("[ilgeniodellostreaming] findvideos")

    data = scrapertools.cache_page(item.url)

    patron = '<td><a class="link_a" href="(.*?)" target="_blank">'
    matches = re.compile(patron, re.DOTALL).findall(data)
    for url in matches:
        html = scrapertools.cache_page(url, headers=headers)
        data += str(scrapertools.find_multiple_matches(html, 'window.location.href=\'(.*?)\''))

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(
            ['[COLOR azure][[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.fulltitle])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist
'''