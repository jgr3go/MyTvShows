
class Season():
    def __init__(self, showName, seasonData, doProcess = False):
        self.__showName = showName
        self.__seasonData = seasonData
        self.__seasonNumber = 0
        self.__episodes = {}
        self.__isProcessed = False
        self.__lastAiredEpisodeNumber = 0
        
        self.__seasonNumber = self.__getSeasonNumber()
        
        if (doProcess == True):
            self.__process()
        
        
    def __str__(self):
        sstr =  'Season' + \
                '\nShow Name     : ' + self.__showName + \
                '\nSeason Number : ' + str(self.seasonNumber) + \
                '\nEpisodes      : ' + str(len(self.__episodes))
                
        return sstr
    
    def __process(self):
        import re
        
        self.__processEpisodes()
        self.__isProcessed = True
        
    def __processEpisodes(self):
        import re
        from Episode import Episode
        from Wiki import Wiki, WikiLookupError
        
        seasonData = self.__seasonData
        
        deeplink = self.__getSeasonDeeplink()
        if (deeplink != None):
            wiki = Wiki()
            seasonData = wiki.query(deeplink)
            self.__seasonData = seasonData
            
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
                
                self.__processEpisodeData(episodeStart, episodeEnd)
                
                episodeStart = episodeEnd
            
            
        except StopIteration:
            episodeEnd = len(self.__seasonData) - 1
            self.__processEpisodeData(episodeStart, episodeEnd)
            pass
    
    def __processEpisodeData(self, episodeStart, episodeEnd):
        from Episode import Episode
        from datetime import date
        
        episodeData = self.__seasonData[episodeStart : episodeEnd]
        episode = Episode(self.__showName, self.__seasonNumber, episodeData)
        self.__episodes[episode.episodeNumber] = episode 
        
        if (episode.airDate != None):
            now = date.today()
            episodeDate = episode.airDate
            
            # if the episode is in the past
            if (now > episodeDate):
                # if we don't have an episode yet, store this episode
                if (self.__lastAiredEpisodeNumber == 0):
                    self.__lastAiredEpisodeNumber = episode.episodeNumber
                # otherwise make sure this date is later than the one we have stored
                latestDate = self.__episodes[self.__lastAiredEpisodeNumber].airDate
                if (latestDate < episodeDate):
                    self.__lastAiredEpisodeNumber = episode.episodeNumber
                    
                
        
        
    
    def __getSeasonNumber(self):
        import re
        
        seasonNumber = re.search('===\s*Season\s*([0-9]+).*===', self.__seasonData)
        if (seasonNumber):
            return int(seasonNumber.group(1))
        else:
            return None
    
    def __getSeasonDeeplink(self):
        import re
        
        deeplink = re.search('{{:(' + self.__showName + '.*)}}', self.__seasonData)
        if (deeplink):
            return deeplink.group(1)
        else:
            return None
        
        
    def getEpisode(self, episodeNumber):
        if (self.__isProcessed == False):
            self.__process()
            
        return self.__episodes[episodeNumber]
    
    def getNumEpisodes(self):
        if (self.__isProcessed == False):
            self.__process()
            
        return len(self.__episodes)
    
    def getSeasonNumber(self):
        return self.__seasonNumber
    
    def getLastAiredEpisode(self):
        if (self.__isProcessed == False):
            self.__process()
            
        if (self.__lastAiredEpisodeNumber == 0):
            raise SeasonError('There are no aired episodes from this season')
        else:
            return self.__episodes[self.__lastAiredEpisodeNumber]
        
    
    
    
class SeasonError(Exception):
    def __init__(self, emsg):
        self.emsg = emsg
    def __str__(self):
        return repr(self.emsg)
    