from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from requester import Requester
from toolbox import format_partial_url
import re

import time

class Parser(object):
    '''Get all useful information by this parser
    
    Use 3 level tracers to locate and return the useful information:
    1. traceBlock(): get news article blocks. Different news topic exists in different blocks. Could be none
    2. traceElements(): must exists, get news article elements
    3. traceInfo(): must exists, get the useful info in the web elements
    All those tracers can be used indivisually without calling parse() method, this is convenient for testing and 
    provide flexibility
    
    Use selenium to load html which is implemented with js/ajax:
    '''
    
    def __init__(self, html=''):
        # Store all data
        self.usefulInfoDicts = []
        self.html_to_bs(html)
    
    def parse(self, site):
        '''parse info
        
        Args:
            html: text file for the page
            site: newsWebsite class object
            
        Returns:
            usefulInfoDicts: array, dicts of each news's useful information
            
        '''
        
        print(f'---------\ngetting info from {site}')
        
        # Get news blocks if it's needed
        if not site.articleBlock:
            print('tracing without blocks\n----------')
            self.trace(self.bs, site)
        else:
            articleBlock = self.traceBlock(self.bs, site.articleBlock)
    
            # Get js content using selenium
            if articleBlock == None:
                print('Trying js loader to get html\n!Warning: check if your tracers are good\n----------\n')
                html = Requester().jsHtmlLoader(url=site.rootURL)
                self.html_to_bs(html)
                
                articleBlock = self.traceBlock(self.bs, site.articleBlock)
                
            # print(f'Getting news article from block: {articleBlock}')
            print('successfully get block')
            self.trace(articleBlock, site)
                
        return self.usefulInfoDicts
    
    def html_to_bs(self, html):
        self.bs = BeautifulSoup(html, 'html.parser')
        
    def trace(self, bs='', site=''):
        '''Trace useful information from article element
        
        Args:
            bs: bs object, could be a news block or the entire page
            site: the site to scrape
            
        Returns:

        '''
        # Get all news elements
        newsElements = self.traceElements(bs, site.articleElement)
        
        # Parse and return news block data
        for newsElement in newsElements: # web element
            # Store each news block data
            usefulInfoDict = {
                'title': '',
                'link': '',
                'img_link': '',
                'source': '',
            }   
            
            print('now getting title:')
            usefulInfoDict['title'] = self.traceInfo(newsElement, site.articleTitle) if site.articleTitle else None
            
            # clean the link before add it to data
            print('now getting link:')
            link = self.traceInfo(newsElement, site.articleLink) if site.articleLink else None
            usefulInfoDict['link'] = format_partial_url(root_url=site.rootURL, new_url=link)
            
            print('now getting image link')
            usefulInfoDict['img_link'] = self.traceInfo(newsElement, site.articleImgLink) if site.articleImgLink else None
            
            print('now getting source')
            usefulInfoDict['source'] = self.traceInfo(newsElement, site.articleSource) if site.articleSource else None
            
            # If there is no title or link available, discard the dict 
            if usefulInfoDict['title']==None or usefulInfoDict['link']==None:
                print('Discard a None Dict')
            else:
                self.usefulInfoDicts.append(usefulInfoDict)
            
    def traceBlock(self, bs='', tracers=''): # tracers: [{}, {}, {},...]
        '''Trace news blocks
        
        Tracer used in here does not use reccursion.
        Each tracer will yield a block element.
        Block content could loaded by js, thus 
        
        Args:
            bs: bs object webpage
            tracers: tracers to retreive the block
        
        Returns:
            block: bs object, contraining all news elements in this block
        '''
        
        print('| tracing block now: |')
        
        if bs == '':
            bs = self.bs
            
        block = None
        
        if not bs:
            print('!!!error: nothing comes from requester to get blocks')
            return None
        else: 
            for tracer in tracers:
                # print(f'tracing article block: {tracer}')
                try:
                    if len(tracer.items()) != 1: # tracer: {'tag':'xxx', 'class':'xxx'}
                        attr = list(tracer.items())[1]
                        block = bs.find(tracer['tag'], {attr[0]: attr[1]})
                    elif 'tag' in tracer.items():
                        block = bs.find(tracer['tag'])
                except RuntimeError as e:
                    print(e)
                    return None
                
        # print(f'tracer completed: {block}\n')
        if not block:
            print('<no block found, check your tracers>')
            return None
        
        return block
        
    def traceElements(self, bs='', tracers=''):
        '''Get all elements in page
        
        Args:
            bs: bs html file of the webpage
            tracers: array, contains dict for BeautifulSoup to parse and returns the data
        
        Returns:
            elements: array, all needed news block elements on webpage
        '''
        
        print('| tracing elements now: |')
        
        if bs == '':
            bs = self.bs
        
        elements = []
        
        # trace news blocks with different tracer
        if not bs:     
            print('!!!error: nothing comes from block element')
            return None
        else:
            for tracer in tracers:
                # print(f'tracing element by: {tracer}')    
                try:
                    if len(tracer.items()) != 1:
                        # 这个地方涉及到了字典的遍历访问，for访问不适用
                        attr = list(tracer.items())[1]
                        elements = bs.find_all(tracer['tag'], {attr[0]: re.compile(f'{attr[1]}.*')})
                    else:
                        elements = bs.find_all(tracer['tag'])
                except RuntimeError as e:
                    print(e)
                    return None
        
        print(f'tracing web element complete: {elements}\n-----\n')
        if not elements:
            print('<No elements found, check your tracers>')
            return None
        
        return elements
 
    def traceInfo(self, element='', tracers=''):
        '''Trace and get useful info
        Use tracers iterating to dest information, return the useful information 
        This method ensures that you can find certain element given html file
        
        Args: 
            element: array, news element block
            tracers: array, contains dict for BeautifulSoup to parse and returns the data

        Returns:
            element: string, not web element, but useful info
        '''
        
        print('| tracing information now |')
        
        if element == '':
            element = self.bs
        
        # Use recursion to get info
        for tracer in tracers: # tracer is a dict {'tag': 'div'} / {'class': 'title'}
            if not element: # due to recursion, the None judgement has to be inside
                print(f'!!!error: nothing comes from web element\n{element}-----\n')
                return None
            else:
            # print(f'traceing info using {tracer} from {element} ')
                try:
                    # Locate element by: tag + attr / attr / tag
                    if len(tracer.items()) != 1:
                        attr = list(tracer.items())[1] # attr: ('class', 'label')
                        element = element.find(tracer['tag'], {attr[0]: attr[1]})
                        print(element)
                    elif 'tag' in tracer.keys():
                        element = element.find(tracer['tag'])
                    else:
                        element = element[tracer['attr']]
                except RuntimeError as e: 
                    print(e)
                    return None
        
        # Element could be BS element / str / None
        if not element:
            print('<No info found, please check your tracers>')
            return None       

        print(f'tracing info complete\n-----')
        # 学会了如何判断类型
        return element.strip() if isinstance(element, str) else element.get_text().strip()
    