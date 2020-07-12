# all_news_titles
Based on BeautifulSoup, requests, Selenium & sqlite. You can add as many websites as you want.

I write this to get news titles for Topic Modeling. However I can't do the Topic Modeling because I just can't. So I upload this for furture usuage when I'm capable to finish my project. I'm not a professional for python scraping but I try to make this simple and suitable for extension and I will keep refactor and refine those codes.

## usage
Run run.py in the folder and get all the news infromation in your database --> sqlite.db

## configuration
- The websites.py under spider folder is where you add any news website you want for scraping. Also remember to add your new classes in scraping --> spider.py
- You can set how many web pages you want in scraping --> utils --> handler.py
- See scraping --> utils --> requester.py for proxy settings. Proxy pool's main folder should be extracted just under scraping folder and I recommand using this: https://github.com/Python3WebSpider/ProxyPool
- Set Selenium to headless mode under scraping --> utils --> requester.py --> jsHtmlLoader

If you feel this intereting, very welcome to pull requests as I'm very troubled by by those deep learning stuff now. 改日再翻译中文。
