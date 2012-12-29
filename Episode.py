class Episode():
    def __init__(self, showName, seasonNumber, episodeData):
        self.__showName = showName
        self.__episodeData = episodeData
        self.seasonNumber = seasonNumber
        self.episodeNumber = 0
        self.episodeTitle = ''
        self.airDate = ''
        self.__isProcessed = False
        
        self.__process()
        
    def __str__(self):
        estr = '\nShowName       : ' + self.__showName + \
               '\nSeason Number  : ' + str(self.seasonNumber) + \
               '\nEpisode Number : ' + str(self.episodeNumber) + \
               '\nEpisode Title  : ' + self.episodeTitle + \
               '\nAir Date       : ' + str(self.airDate)
        
        return estr
    
    def __process(self):
        import re
        
        self.episodeNumber = self.__getEpisodeNumber()
        self.episodeTitle = self.__getEpisodeTitle()
        self.airDate = self.__getAirDate()
        self.__isProcessed = True
            
        
        
    def __getEpisodeNumber(self):
        import re
        episodeNumber = re.search('\|\s*EpisodeNumber2\s*\=\s*([0-9]+)', self.__episodeData)
        if (episodeNumber):
            return int(episodeNumber.group(1))
        else:
            return None
        
    def __getEpisodeTitle(self):
        import re
        
        episodeTitle = re.search('\|\s*Title\s*\=(.*)', self.__episodeData)
        if (episodeTitle == None):
            return ''
        
        episodeTitle = episodeTitle.group(1).strip()
        
        # replace '[[link address | link name]]...' with 'link name...'
        epFormat = re.search('\[\[.*\|(.*)\]\](.*)', episodeTitle)
        if (epFormat):
            episodeTitle = epFormat.group(1) + epFormat.group(2)
        
        # replace '[[link name]]...' with 'link name...'
        epFormat = re.search('\[\[(.*)\]\](.*)', episodeTitle)
        if (epFormat):
            episodeTitle = epFormat.group(1) + epFormat.group(2)
            
        # replace comma space with comma
        episodeTitle = episodeTitle.replace(' ', '.')
        
        episodeTitle = episodeTitle.replace(':', '-')
        episodeTitle = episodeTitle.replace('/', '-')
        episodeTitle = episodeTitle.replace('"', '\'')
        episodeTitle = episodeTitle.replace('?', '')
        episodeTitle = episodeTitle.replace('*', '')
        episodeTitle = episodeTitle.replace('\\', '')
        episodeTitle = episodeTitle.replace('<', '')
        episodeTitle = episodeTitle.replace('>', '')
        episodeTitle = episodeTitle.replace('|', '')
        
        # and replace the ones we just made
        episodeTitle = episodeTitle.replace(',.', ',')
        episodeTitle = episodeTitle.replace('..', '.')
        
        return episodeTitle
        
    def __getAirDate(self):
        import re
        from datetime import date
        
        airDateFull = re.search('\|\s*OriginalAirDate\s*\=(.*)', self.__episodeData)
        if (airDateFull == None):
            return None
        
        airDateData = airDateFull.group(1)
        
        #expect Air Date to look like {{Start date|yyyy|m|d}}
        airDate = re.search('\s*{{Start date\|([0-9]+)\|([0-9]+)\|([0-9]+)}}', airDateData)
        if (airDate == None):
            return None
        
        epYear = int(airDate.group(1))
        epMonth = int(airDate.group(2))
        epDay = int(airDate.group(3))
        
        return date(epYear, epMonth, epDay)
    
    
    def getSearchString(self):
        sstr = self.__showName + ' '
        
        epstr = 's'
        if (self.seasonNumber < 10):
            epstr += '0'
        epstr += repr(self.seasonNumber) + 'e'
        if (self.episodeNumber < 10):
            epstr += '0'
        epstr += repr(self.episodeNumber)
        
        sstr += epstr
        
        return sstr
    
    def getShowName(self):
        return self.__showName
        
                            