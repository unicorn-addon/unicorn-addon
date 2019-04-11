# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Unicorn / XBMC Plugin
# Canale per ilgeniodellostreaming
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

__channel__ = "ilgeniodellostreaming"
host = "https://ilgeniodellostreaming.pw"

headers = [
    ['User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'],
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
                     url="%s/film/" % host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/movie_new.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Anno[/COLOR]",
                     action="peliculas_year",
                     url=host,
                     extra="movie",
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/movie_year.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Film[COLOR orange] - Archivio A-Z[/COLOR]",
                     action="peliculas_az_list",
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
                     url="%s/serie/" % host,
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/serie.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Serie TV[COLOR orange] - Aggiornate[/COLOR]",
                     action="peliculas_tvnew",
                     url="%s/aggiornamenti-serie/" % host,
                     thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/serie_new.png"),
                Item(channel=__channel__,
                     title="[COLOR azure]Anime[COLOR orange] - Novita[/COLOR]",
                     action="peliculas_anime",
                     url="%s/anime/" % host,
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

# ======================================================================================================================

def newest(categoria):
    logger.info("[ilgeniodellostreaming] newest" + categoria)
    itemlist = []
    item = Item()
    try:
        if categoria == "peliculas":
            item.url = "%s/film/" % host
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

def categorias(item):
    logger.info("[ilgeniodellostreaming] categorias")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    bloque = scrapertools.get_match(data, '<h2>Genere</h2>(.*?)</ul></div>')

    # Extrae las entradas (carpetas)
    patron = '<li class="cat-item.*?href="(.*?)" >(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(bloque)

    for scrapedurl, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas",
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/movie_genre.png",
                 folder=True))

    return itemlist


# ==================================================================================================================================================

def search(item, texto):
    logger.info("[ilgeniodellostreaming] " + item.url + " search " + texto)
    item.url = host + "/?s=" + texto

    if item.extra == "movie":
        return peliculas_search_movie(item)

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
    #data = scrapertools.cache_page(item.url)
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = r'thumbnail animation-2.*?<a href="(.*?)".*?src="(.*?)".*?tvshows">(.*?)<.*?href.*?>(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, genere, scrapedtitle in matches:
        scrapedplot = ""
        scrapedthumbnail = httptools.get_url_headers(scrapedthumbnail)
        scrapedtitle = scrapertools.decodeHtmlentities(scrapedtitle)
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos" if not "tvshow" in item.extra else "season",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_search_movie(item):
    logger.info("[ilgeniodellostreaming] peliculas_search_movie")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = r'thumbnail animation-2.*?<a href="(.*?)".*?src="(.*?)".*?title">.*?>(.*?)<.*?p>(.*?)</'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra='movie',
                 folder=True))

    return itemlist

# ==================================================================================================================================================
def peliculas(item):
    logger.info("[ilgeniodellostreaming] peliculas")
    itemlist = []

    # Descarga la pagina
    #data = httptools.downloadpage(host + dict[0]["url"])  # Para que pueda saltar el cloudflare, se tiene que descargar la página completa
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = r'"item movies".*?href="(.*?)".*?src="(.*?)".*?h3>.*?>(.*?)<.*?texto">(.*?)<'
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
                 extra="movie",
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
                 extra="movie",
                 thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/next.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================
def peliculas_anime(item):
    logger.info("[ilgeniodellostreaming] peliculas_anime")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = r'"item tvshows".*?href="(.*?)".*?src="(.*?)".*?h3>.*?>(.*?)<.*?texto">(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle, scrapedplot in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="season",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra="tvshow",
                 folder=True))

    # Extrae el paginador
    patronvideos = '<span class=\"current">.*?<a href=\'([^\']+)\''
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_anime",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 extra="tvshow",
                 thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/next.png",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_az_list(item):
    logger.info("[ilgeniodellostreaming] peliculas_az_list")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = r'class="btn btn-letter.*?title="(.*?)".*?href="(.*?)"'
    matches = re.compile(patron, re.S).findall(data)

    for scrapedtitle, scrapedurl in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_az",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] ",
                 url=scrapedurl + "/page/1/",
                 extra="movie",
                 folder=True))
    return itemlist

# ==================================================================================================================================================

def peliculas_az(item):
    logger.info("[ilgeniodellostreaming] peliculas_az")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = r'<td class=\"mlnh-thumb\"><a href=\"(.*?)\".*?<img src=\"([^\"]+)\".*?<a.*?>(.*?)</a>'
    matches = re.compile(patron, re.S).findall(data)

    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR] ",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 extra="movie",
                 folder=True))

    # Extrae el paginador
    patronvideos = r'<span class=\"current">.*?<a href=\'([^\']+)\''
    matches = re.compile(patronvideos, re.DOTALL).findall(data)

    if len(matches) > 0:
        scrapedurl = urlparse.urljoin(item.url, matches[0])
        itemlist.append(
            Item(channel=__channel__,
                 action="peliculas_az",
                 title="[COLOR orange]Successivi >>[/COLOR]",
                 url=scrapedurl,
                 thumbnail="https://raw.githubusercontent.com/unicorn-addon/unicorn-addon/master/images/channels_icons/next.png",
                 extra="movie",
                 folder=True))

    return itemlist

# ==================================================================================================================================================

def peliculas_year(item):
    logger.info("[ilgeniodellostreaming] peliculas_year")
    itemlist = []

    # Scarica la pagina
    data = httptools.downloadpage(item.url).data

    # Prende il blocco interessato
    blocco = r'<ul class="year scrolling">(.*?)</ul>'
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
                 url=scrapedurl,
                 folder=True))
    return itemlist

# ==================================================================================================================================================

def peliculas_tv(item):
    logger.info("[ilgeniodellostreaming] peliculas_tv")
    itemlist = []

    # Descarga la pagina
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = r'<div class="poster"><a href="(.*?)">.*?src="(.*?)".*?h3>.*?>(.*?)<.*?"texto">(.*?)<'
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
                 action="season",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 folder=True))

    # Extrae el paginador
    patronvideos = r'<span class=\"current">.*?<a href=\'([^\']+)\''
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
    data = httptools.downloadpage(item.url).data

    # Extrae las entradas (carpetas)
    patron = r'<div class="poster"><img src="(.*?)".*?<a href="(.*?)".*?n; ">(.*?)<.*?"serie">(.*?)<'

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
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=scrapedthumbnail,
                 plot=scrapedplot,
                 extra='tvshow',
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

def season(item):
    logger.info("[ilgeniodellostreaming] season")
    itemlist = []

    data = httptools.downloadpage(item.url).data

    patron = r'"title">(.*?)<(.*?)</span><span class='
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

    patron = r'"numerando">(.*?)<.*?href="(.*?)">(.*?)<'
    matches = re.compile(patron, re.DOTALL).findall(data)

    for scrapednumber, scrapedurl, scrapedtitle in matches:
        scrapedtitle = scrapednumber +" - " + scrapedtitle
        itemlist.append(
            Item(channel=__channel__,
                 action="findvideos",
                 fulltitle=scrapedtitle,
                 show=scrapedtitle,
                 title="[COLOR azure]" + scrapedtitle + "[/COLOR]",
                 url=scrapedurl,
                 thumbnail=item.thumbnail,
                 plot=item.plot,
                 extra = "tvshow",
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

def findvideos(item):
    logger.info("[ilgeniodellostreaming] findvideos")

    if item.extra == "movie":
        data = httptools.downloadpage(item.url).data
        patron = r'class=\"link_a\" href=\"([^\"]+)\" target=.*?<img.*?>(.*?)<'
        matches = re.compile(patron, re.DOTALL).findall(data)

        itemlist = []

        for match in matches:
            url = match[0]
            title = match[1]

        data = httptools.downloadpage(url).data
        patron = r'class="boton reloading".*?href="(.*?)"'
        matches = re.compile(patron, re.DOTALL).findall(data)
        title = title
        title = title.replace(" ","")

        for scrapedurl in matches:
            itemlist.append(Item(
                channel=__channel__,
                #title="".join(['[COLOR azure][[COLOR orange]' + item.title.strip().capitalize() + '[/COLOR]] - ', item.fulltitle]),
                title='[COLOR azure][[COLOR orange]'+title+'[/COLOR]]'+' - '+item.fulltitle,
                url=scrapedurl,
                action="play",
                show=item.show
            ))

        return itemlist

    if item.extra == "tvshow":
        data = httptools.downloadpage(item.url).data
        patron = r'<iframe.*?src=\"([^\"]+)\".*?allow'
        matches = re.compile(patron, re.DOTALL).findall(data)

        itemlist = servertools.find_video_items(data=data)
        for videoitem in itemlist:
            videoitem.title = '[COLOR azure][COLOR orange][' + videoitem.title + '][/COLOR]' + ' ' + item.title + '[/COLOR]'
            videoitem.fulltitle = item.fulltitle
            videoitem.thumbnail = item.thumbnail
            videoitem.show = item.show
            videoitem.plot = item.plot
            videoitem.channel = __channel__

        return itemlist

    data = item.url
    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[COLOR azure][[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.fulltitle])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.plot = item.plot
        videoitem.channel = __channel__

    return itemlist

# ==================================================================================================================================================

def play(item):
    logger.info("[ilgeniodellostreaming] play: %s" % item.url)

    url = item.url

    from lib import unshortenit
    url, status = unshortenit.unshorten(url)

    itemlist = servertools.find_video_items(data=url)

    for videoitem in itemlist:
        servername = re.sub(r'[-\[\]\s]+', '', videoitem.title)
        videoitem.title = "".join(['[COLOR azure][[COLOR orange]' + servername.capitalize() + '[/COLOR]] - ', item.show])
        videoitem.fulltitle = item.fulltitle
        videoitem.show = item.show
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist