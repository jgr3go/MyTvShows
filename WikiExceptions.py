class WikiError(Exception):
    def __init__(self, emsg):
        self.emsg = emsg
    def __str__(self):
        return repr(self.emsg)


class WikiLookupError(Exception):
    def __init__(self, emsg):
        self.emsg = emsg
    def __str__(self):
        return repr(self.emsg)
    
class Season():
    def __init__(self, showName):
        self.__showName = showName
        self.seasonNumber = 0
        self.episodes = []
        
    def __str__(self):
        sstr =  'Season' + \
                '\nShow Name     : ' + self.__showName + \
                '\nSeason Number : ' + str(self.seasonNumber) + \
                '\nEpisodes      : ' + str(len(self.episodes))
                
        return sstr

        
class Episode():
    def __init__(self, showName):
        self.__showName = showName
        self.seasonNumber = 0
        self.episodeNumber = 0
        self.episodeTitle = ''
        self.airDate = ''
        
    def __str__(self):
        estr = 'Episode' + \
               '\nShowName       : ' + self.__showName + \
               '\nSeason Number  : ' + str(self.seasonNumber) + \
               '\nEpisode Number : ' + str(self.episodeNumber) + \
               '\nEpisode Title  : ' + self.episodeTitle + \
               '\nAir Date       : ' + str(self.airDate)
        
        return estr
        
    
class Wiki():
    def __init__(self, showName):
        self.__showName = showName
        self.__queryName = 'List of ' + showName + ' episodes'
        self.__showData = None
        self.__allSeasons = {}
        self.__allSeasonsData = []
        self.__numSeasons = 0
        
        self.getShowData()
        
    def __queryWiki(self, titleName):
        import urllib2
    
        baseUrl = 'http://en.wikipedia.org/w/api.php?'
        # I'm making a query for info
        action = '&action=query'
        # I want the most recent revision
        prop = '&prop=revisions'
        # format = xml for now, also json, dump, txt, etc
        resultFormat = '&format=xml'
        # I want the content of the page (as opposed to comments, editor, etc)
        rvprop = '&rvprop=content'
        # I want redirects resolved for me
        redirects = '&redirects='
        # This is the list of titles that I want, for now, I'll do one at a time
        titles = '&titles=' + urllib2.quote(titleName)
    
        fullUrl = baseUrl+action+prop+resultFormat+rvprop+redirects+titles
        
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        apiResponse = opener.open(fullUrl)
        page = apiResponse.read()
        return page
    
    
    def __processWikiResponse(self, wikiResponse):
        from bs4 import BeautifulSoup
        from bs4 import element
        
        responseXML = BeautifulSoup(wikiResponse, 'xml')
        pages = responseXML.pages
        if (len(pages) != 1):
            raise WikiError('No response returned from Wikipedia')
        
        page = pages.page
        if page.get('missing') != None:
            raise WikiLookupError('\'' + showListName + '\' was not found in Wikipedia')
            
        self.__showData = unicode(page.revisions.rev.string.encode('ascii', 'ignore'))
        return self.__showData
    
    
    def __processShowData(self):
        import re
        
        self.getShowData()
        
        seasonRegex = re.compile('===\s*Season')
        foundSeasons = seasonRegex.finditer(self.__showData)
        if (foundSeasons == None):
            raise WikiLookupError('Could not find \'===Season\' tag in article')
        
        
        try:
            seasonIdx = foundSeasons.next()
            seasonStart = seasonIdx.start()
            
            while (1):
                seasonIdx = foundSeasons.next()
                seasonEnd = seasonIdx.start()
                
                self.__allSeasonsData.append(self.__showData[seasonStart:seasonEnd])
                
                seasonStart = seasonEnd
            
        except StopIteration:
            self.__allSeasonsData.append(self.__showData[seasonStart : len(self.__showData) - 1])
            self.__numSeasons = len(self.__allSeasonsData)
        
        self.__processSeason(self.__numSeasons)
        
        
    def __processSeason(self, seasonNumber):
        import re
        
        seasonIndex = seasonNumber - 1
        seasonData = self.__allSeasonsData[seasonIndex]
        season = Season(self.__showName)
        season.seasonNumber = self.__getSeasonNumber(seasonData)
        self.__allSeasons[season.seasonNumber] = season
        
        self.__processEpisodes(season.seasonNumber)
        
    def __processEpisodes(self, seasonNumber):
        import re
        
        season = self.__allSeasons[seasonNumber]
        seasonData = self.__allSeasonsData[seasonNumber - 1]
        deeplink = self.__getSeasonDeeplink(seasonData)
        
        if (deeplink != None):
            seasonDataRaw = self.__queryWiki(deeplink)
            seasonData = self.__processWikiResponse(seasonDataRaw)
            self.__allSeasonsData[seasonNumber - 1] = seasonData
            
        episodeRegex = re.compile('{{Episode list', re.IGNORECASE)
        foundEpisodes = episodeRegex.finditer(seasonData)
        
        if (foundEpisodes == None):
            raise WikiLookupError('Could not find \'{{Episode List\' tag')
    
        episodeStart = 0
        try:
            episodeIndex = foundEpisodes.next()
            episodeStart = episodeIndex.start()
            
            while (1):
                episodeIndex = foundEpisodes.next()
                episodeEnd = episodeIndex.start()
                
                episodeData = seasonData[episodeStart : episodeEnd]
                episode = self.__processEpisode(episodeData, self.__showName, season.seasonNumber)
                season.episodes.append(episode)
                #print episode
                
                episodeStart = episodeEnd
            
            
        except StopIteration:
            #print seasonData[episodeStart : len(seasonData) - 1]
            pass
        
        
        
    def __processEpisode(self, episodeData, showName, seasonNumber):
        import re
        
        episode = Episode(showName)
        episode.seasonNumber = seasonNumber
        episode.episodeNumber = self._getEpisodeNumber(episodeData)
        episode.episodeTitle = self._getEpisodeTitle(episodeData)
        episode.airDate = self._getAirDate(episodeData)
        return episode
        
        
    
    def getShowData(self):
        if (self.__showData == None):
            wikiResponse = self.__queryWiki(self.__queryName)
            self.__processWikiResponse(wikiResponse)
            self.__processShowData()
        
        return self.__showData
    
        
    def __getSeasonNumber(self, seasonData):
        import re
    
        seasonNumber = re.search('===\s*Season\s*([0-9]+).*===', seasonData)
        if (seasonNumber):
            return int(seasonNumber.group(1))
        else:
            return None
    
    def getSeason(self, seasonNumber):
        try :
            return self.__allSeasons[seasonNumber]
        
        except IndexError:
            self.__processSeason(seasonNumber)    
            return self._allSeasons[seasonNumber]
    
    def getLastSeason(self):
        if (self.__numSeasons == 0):
            raise LookupError('Could not find any seasons')
        
        return self.getSeason(self.__numSeasons)
    
    
    def __getSeasonDeeplink(self, seasonData):
        import re
        
        deeplink = re.search('{{:(' + self.__showName + '.*)}}', seasonData)
        if (deeplink):
            return deeplink.group(1)
        else:
            return None

    def _getEpisodeNumber(self, episodeData):
        import re
        episodeNumber = re.search('\|\s*EpisodeNumber2\s*\=\s*([0-9]+)', episodeData)
        if (episodeNumber):
            return int(episodeNumber.group(1))
        else:
            return None
        
    def _getEpisodeTitle(self, episodeData):
        import re
        
        episodeTitle = re.search('\|\s*Title\s*\=\s*(.*)', episodeData)
        if (episodeTitle):
            return episodeTitle.group(1)
        else:
            return ''
        
    def _getAirDate(self, episodeData):
        import re
        from datetime import date
        
        airDateFull = re.search('\|\s*OriginalAirDate\s*\=(.*)', episodeData)
        if (airDateFull == None):
            return None
        
        airDateData = airDateFull.group(1)
        
        #expect Air Date to look like {{Start date|yyyy|m|d}}
        airDate = re.search('\s*{{Start date\|([0-9]+)\|([0-9]+)\|([0-9]+)}}', episodeData)
        if (airDate == None):
            return None
        
        epYear = int(airDate.group(1))
        epMonth = int(airDate.group(2))
        epDay = int(airDate.group(3))
        
        return date(epYear, epMonth, epDay)
                            
        
        