import datetime

# data from spider: [{'title': 'xxx', 'link': 'xxx',...}, {...}, {...}]
# data for sqlite: [(title, link, img_link, source, added_date), (), (), ()]
def format_data_for_each_website(data): 
    '''Format scraping data into tuples that could be used by database core moduel
    
    By default, those data will also be reversed, so they will be in descent order
    of their published time
    
    Args:
        data: webisite news data scraped from the websites
        
    Returns:
        data_for_database: data used for insersion in database
    '''
    data_for_database = list()
    
    # get utc datetime precise to seconds
    date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # reversed data transformation
    for d in reversed(data): 
        # add timestamp for sqlite here, use UTC time
        data_segment = (d['title'], d['link'], d['img_link'], d['source'], date_time)
        if data_segment != None:
            data_for_database.append(data_segment)
            
    if len(data) == len(data_for_database):
        return data_for_database
    else:
        print('!Unable to match data when formatting')