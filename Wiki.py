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
    

    
class Wiki():
    def __init__(self):
        pass
    
    def query(self, queryString):
        wikiResponse = self.__queryWiki(queryString)
        processedResponse = self.__processWikiResponse(queryString, wikiResponse)
        return processedResponse
        
    
    def __queryWiki(self, queryString):
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
        titles = '&titles=' + urllib2.quote(queryString)
    
        fullUrl = baseUrl+action+prop+resultFormat+rvprop+redirects+titles
        
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        apiResponse = opener.open(fullUrl)
        page = apiResponse.read()
        return page
    
    
    def __processWikiResponse(self, queryString, wikiResponse):
        from bs4 import BeautifulSoup
        from bs4 import element
        
        responseXML = BeautifulSoup(wikiResponse, 'xml')
        pages = responseXML.pages
        if (len(pages) != 1):
            raise WikiError('No response returned from Wikipedia')
        
        page = pages.page
        if page.get('missing') != None:
            raise WikiLookupError('\'' + queryString + '\' was not found in Wikipedia')
            
        responseData = unicode(page.revisions.rev.string.encode('ascii', 'ignore'))
        return responseData
    
        