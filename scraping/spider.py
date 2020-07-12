import sys
sys.path.append('.')

from scraping.websites import guanchaWorld
from scraping.websites import huanqiuWorld
from scraping.websites import thepaperShiShi
from scraping.websites import cankaoxiaoxiWorld
from scraping.websites import peopleWorld
from scraping.websites import qqWorld
from scraping.websites import news163World
from scraping.websites import sinaWorld


from scraping.utils.handler import PageHandler


'''Scraping news and return all data: [{}, {}, {}, {}]
1. title
2. link
3. date
TODO: category, id
'''

def pipeline():
    sites = [cankaoxiaoxiWorld, thepaperShiShi, huanqiuWorld, guanchaWorld, peopleWorld, qqWorld, news163World, sinaWorld]
    for site in sites:
        # you must call a method to get its return value
        try:
            data = PageHandler(site).handlePage()
            print(f'{site.websiteName}: {data}\n')
            yield (site.websiteName, data)
        except:
            print(f'||| {site.websiteName} failing to scrape |||')

if __name__ == "__main__":
    for data in pipeline():
        print(data)