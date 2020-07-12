import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.common.exceptions import NoSuchElementException as NSEE

import time
from toolbox import get_random_proxy
from toolbox import test_proxy_ip

'''
When you setting up proxies, you need to set up both
https and http proxy for http and https website
'''


class Requester:
    def __init__(self, headers = {'Method': 'GET',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'}):
        self.headers = headers

    def getPage(self, url, use_proxy=False):
        '''scraping site

        Args:
            URL: webpage url to scrape
            headers: headers info to simulate browser request

        Returns:
            html text file
        '''
        
        proxies = None
        
        if use_proxy:
            proxy_ip = self.get_proxy_ip()
            if proxy_ip != None:
                proxies = {
                    'http': f'http://{proxy_ip}',
                    'https': f'https://{proxy_ip}'
                }
                
            print(f'requesting with proxy: {proxy_ip}')

        print(f'requesting: {url}')

        r = requests.get(url, headers=self.headers, proxies=proxies)
        r.raise_for_status()
        r.encoding = r.apparent_encoding

        print('requesting successful')
        return r.text

    def jsHtmlLoader(self, url, scroll=False, scroll_num=3, click=False, click_num=3, click_path='', turn=False, waitTime=1):
        '''Use selenium to get the fully loaded html fiel
        
        Wait and return the html content after a certain amount
        
        Args:
            url: str, rootURL of the root page
            
        Returns:
            html: str, fully loaded html with all ajax content
        '''
        
        # get and set up proxy
        proxy_ip = self.get_proxy_ip()
        
        # check if the proxy is available
        # aval = self.check_proxy_ip(proxy_ip)
        # if aval:
        #     proxy = f'http://{proxy_ip}'
        #     try:
        #         webdriver.DesiredCapabilities.CHROME['proxy'] = {
        #             "httpProxy": proxy,
        #             "proxyType": "MANUAL",
        #         }
        #         print(f'set up proxy for js loader: {proxy}')
        #     except:
        #         print('unable to set up proxy for js loader...') 
        
        if proxy_ip != None:
            try:
                webdriver.DesiredCapabilities.CHROME['proxy'] = {
                    "httpProxy": f'http://{proxy_ip}',
                    'httpsProxy': f'https://{proxy_ip}',
                    "proxyType": "MANUAL",
                }
                print(f'Set up proxy for js loader: {proxy}')
            except:
                print('Uable to set up proxy for js loader...')       
            
        # Set up headless Chrome browser
        options = Options()
        # options.add_argument('--headless')
        options.page_load_strategy = 'eager'
        prefs = {
            'profile.default_content_setting_values': {
                'images': 2,
            }
        }
        options.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome(options=options)
        
        # Request, wait and return the fully loaded html file
        driver.get(url)
        print('Waiting js to load...')
        time.sleep(waitTime)
        
        html = driver.page_source
        
        # If the pagination is to scroll, scroll the page then
        if scroll:
            self.scroll_after_request(driver, scroll_num)
            html = driver.page_source.encode('utf-8')
        
        # If the pagination is to click, click the page for 3 times default
        if click:
            if not turn:
                self.click_after_request(driver, click_num, click_path)
                html = driver.page_source.encode('utf-8')
            if turn:
                html = driver.page_source.encode('utf-8')
                self.click_after_request(driver, 1, click_path)
                next_page_url = driver.current_url
        
        # Close after several tries        
        # if waitTime > 3:
        # driver.close()
        
        # Return the page or load the html again
        if html != None:
            # driver.close()
            return html if not turn else (html, next_page_url)
        else:
            print('Failing to load js...trying again\n')
            # driver.close()
            return self.jsHtmlLoader(url, waitTime+0.5)
            
    def scroll_after_request(self, driver, num):
        scroll_script = "window.scrollTo(0, document.body.scrollHeight);"
        for i in range(num):
            try:
                driver.execute_script(scroll_script)
                time.sleep(0.5)
                print('scrolling down page...')
            except:
                print('There should no more avaliable content\n')
                break
    
    def click_after_request(self, driver, num, path):
        '''Click the button for more button several times
        
        Args:
            driver: the webdriver to do this click
            click_num: how many time to click and load more content
        '''
        
        # Here, we only consider the circumstance that the clickable element positioin is fixed
        # which is usually the case 
        for i in range(num):
            try:
                print(path)
                more_button = driver.find_element_by_xpath(path)
                print(more_button)
                more_button.click()
                print('click to load more page...')
            except NSEE as e:
                print(e)
                print('There should be no more available content\n')
                break
            
    def get_proxy_ip(self):
        '''Get proxy ip address
        
        Returns: 
            proxy_ip: proxy ip address
        '''
        
        # try to get proxy for 3 times
        proxy_ip = get_random_proxy()
        proxy_ip = test_proxy_ip(proxy_ip)
        
        if proxy_ip != None:
            return proxy_ip
        
        print('Failing to fetch valid proxy ip after 3 times, please udpdate your proxy pool!')
