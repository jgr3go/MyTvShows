class Config():
    def __init__(self, configFile):
        self.__configFile = configFile
        self.distributionList = []
        self.distributionSender = ''
        self.distributionSenderPass = ''
        self.listOfAllShows = []
        self.__readConfig__()
        
    def __readConfig__(self):
        from bs4 import BeautifulSoup
        from bs4 import element
        
        configInput = open(self.__configFile,'r')
        config = BeautifulSoup(configInput.read(), "xml" )
        
        distList = config.distributionList
        emails = distList.find_all('email');
        for email in emails:
            self.distributionList.append(email.string)
       
        sender = config.distributionSender
        self.distributionSender = sender.email.string
        self.distributionSenderPass = sender.password.string
        
        showsList = config.shows
        shows = showsList.find_all('showName')
        for show in shows:
            self.listOfAllShows.append(show.string)
        
        
    