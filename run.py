from scraping import spider
from tools import formatter
from database.core import Table

for data in spider.pipeline():
    data_for_each_website = formatter.format_data_for_each_website(data[1])
    
    table = Table(data[0]) # create table with the name of news website

    table.dump_insert(data_for_each_website)
    table.reserve()
    table.close_all()
