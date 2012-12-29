class Show():
    
    def __init__(self, showName, showData, processOnlyLast = True):
        self.__showName = showName
        self.__showData = showData
        self.__seasons = {}
        self.__numSeasons = 0
        self.__process(processOnlyLast)
    
    def __str__(self):
        sstr = 'Show Name    : ' + self.__showName + \
               '\nNum Seasons  : ' + str(self.__numSeasons)
        return sstr
    
    def __process(self, processOnlyLast):
        from Season import Season
        import re
        from WikiExceptions import WikiLookupError
        
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
        
                self.__processSeasonData(seasonStart, seasonEnd)
                
                seasonStart = seasonEnd
                
        except StopIteration:
            seasonEnd = len(self.__showData) - 1
            self.__processSeasonData(seasonStart, seasonEnd)
            self.__numSeasons = len(self.__seasons)
            
    def __processSeasonData(self, seasonStart, seasonEnd):
        from Season import Season
        
        seasonData = self.__showData[seasonStart : seasonEnd]
        season = Season(self.__showName, seasonData)

        self.__seasons[season.getSeasonNumber()] = season
        
    def getSeason(self, seasonNumber):
        return self.__seasons[seasonNumber]
    
    def getNumSeasons(self):
        return self.__numSeasons
    
    def getLastSeason(self):
        return self.getSeason(self.__numSeasons)
    
    def getShowName(self):
        return self.__showName