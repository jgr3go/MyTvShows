#!/usr/bin/python

import smtplib
import os
import string
import sys
from WikiExceptions import WikiLookupError
from WikiExceptions import WikiError
from Config import Config
from WikiExceptions import Wiki
configFile = 'C:\\Users\\Jon\\Projects\\python\\'
emailEpisodes = ''



def sendmail(message, subject):
    from Config import Config
    import smtplib
    
    HOST="smtp.gmail.com"
    PORT=587
    SENDER=config.distributionSender
    SENDERPASS=config.distributionSenderPass

    BODY = string.join(("From: %s" % SENDER,
                        "To: %s" % ', '.join(config.distributionList),
                        "Subject: %s" % subject,
                        "",
                        message), "\r\n")
    
    try:
        server=smtplib.SMTP(HOST, PORT)
        server.ehlo()
        server.starttls()
        server.login(SENDER, SENDERPASS)
        server.sendmail(SENDER,config.distributionList,BODY)
        server.quit()
    except Exception,R:
        return R
    
 
    
def buildAndQueryList():
    
    from Episode import Episode
    from Config import Config
    from Wiki import WikiError, WikiLookupError
    
    for show in config.listOfAllShows:
        try:
            queryName = 'List of ' + show + ' episodes'
            episode = getMostRecentEpisode(show, queryName)
            addEpisodeToEmail(episode)
            
        except WikiLookupError as e:
            print 'Error: <' + show + '>: ' + str(e)
        except WikiError as e :
            print 'Error: <' + show + '>: ' + str(e)
        except Exception as e :
            print 'Error: <' + show + '>: ' + str(e)
    
            
    sendmail(emailEpisodes, 'Show\'s')
            
        

def getMostRecentEpisode(showName, showListName):
    import re
    from datetime import date
    from Wiki import Wiki
    from Show import Show
    from Season import SeasonError
    from Season import Season
    
    wiki = Wiki()
    showData = wiki.query(showListName)
    show = Show(showName, showData)
    
    lastEpisode = None
    lastSeasonNumber = show.getNumSeasons()
    
    
    while (1):
        season = show.getSeason(lastSeasonNumber)
        try :
            lastEpisode = season.getLastAiredEpisode()
            break
        
        except SeasonError as e:
            lastSeasonNumber -= 1
            
        except Exception as e:
            lastEpisode = None
            break
    
    return lastEpisode


def addEpisodeToEmail(episode):
    from Episode import Episode
    
    global emailEpisodes
    emailEpisodes += '\n\n'
    emailEpisodes += str(episode) + '\n'
    emailEpisodes += getSearchLink(episode)
    
    
def getSearchLink(episode):
    import urllib2
    
    slinkpre = 'http://kat.ph/search/'
    slinkpost = '/?from=opensearch'
    
    slink = slinkpre + urllib2.quote(episode.getSearchString()) + slinkpost
    return slink
    

emailEpisodes = ''
config = Config('episodes.cfg')
buildAndQueryList()