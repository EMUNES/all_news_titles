import os
import sys
file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from requester import Requester
from _parser import Parser
from toolbox import format_partial_url
import time

'''Spider handler, in charge of scroll page or change page

This handler will
'''

'''
!WARNING: paginationLoc is diversed
1. when it's an array, its works the same as elements, used like other properties
2. when it's a string, it stands for xpath for selenium to locate the pagination element
'''


class PageHandler(object):
    '''Handle page
    
    Change page by scroll the page or turn to next one
    
    Args:
        url: str, initial page url
        site: website object, the website to scrape
    '''
    
    def __init__(self, site):
        self.site = site
        
    def handlePage(self):
        '''Change page and scrape data
        '''
                
        self.data = list()
                
        if self.site.pageType == 'scroll':
            self.scrollPage()
        if self.site.pageType == 'turn':
            self.turnPage()
        if self.site.pageType == 'click':
            self.clickPage()
        
        print(f'Getting news from {self.site.websiteName}: {self.data}\n')
        return self.data
            
    def scrollPage(self):
        '''Scroll the page and call parser to get the information
        '''
        
        data = None
        url = self.site.start_url
        
        print(f'tring to scroll the page using selenium: {url}')

        try:
            html = Requester().jsHtmlLoader(url=url, scroll=True, scroll_num=self.site.paginationNum)
        except RuntimeError as e:
            print('!Error while using selenium to scroll the page:')
            print(e, '\n')
        
        try:
            data = Parser(html).parse(self.site)
        except RuntimeError as e:
            print('!Error while parsing data from scrolling page:')
            print(e)
        
        self.data = data
            
    def clickPage(self):
        '''Click the page and call parser to parser the page and return the data
        '''
                
        data = None
        url = self.site.start_url
        
        print(f'tring to click the page after loading with selenium: {url}')
        
        try:
            html = Requester().jsHtmlLoader(url=url, click=True, click_num=self.site.paginationNum, click_path=self.site.paginationLoc)
        except RuntimeError as e:
            print('!Error while loading page content with selenium')
            print(e)
            
        try:
            data = Parser(html).parse(self.site)
        except RuntimeError as e:
            print('!Error while parsing data from clickable page')
            print(e)
        
        self.data = data
            
    def turnPage(self):
        '''Turn page and get information from every page
        
        First try to get page url from html content. If not, then try to get it from js
        
        Store info from each page content to local storage
        '''
        
        pageNum = 1

        url = self.site.start_url
                
        while pageNum <= self.site.paginationNum: 
            print(f'Getting information from page: {url}\n page: {pageNum}\n-----\n')

            # Get html for next page
            try:
                # set click_num to 1 to scape one page a time
                html, next_page_url = Requester().jsHtmlLoader(url, click=True, click_num=1, click_path=self.site.paginationLoc, turn=True)
                print(f'getting next page url to turn to: {url}')
            except RuntimeError as e:
                print('!Error while loading page content with selenium')
                print(e)  
            
            # Get data
            try:
                data = Parser(html).parse(site=self.site)
                print(f'Data in page {pageNum}: {data}\n')
            except:
                print('!Error while parsing data in turning page')
            
            # Next page url 
            url = next_page_url
            pageNum += 1
            
            # merge data
            self.data.extend(data)
    