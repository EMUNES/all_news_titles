import requests
import subprocess
import time

def format_partial_url(root_url='', new_url=''):
    '''Clear the link
    
    If there is a condition for page url, concact that page url and return
    If no page number find, return the combination of both url
    
    Args:
        root_url: str, root link
        new_url: str, page link
        
    Returns:
        final: str, cleaned and ready to be used url for next page
    '''
    if new_url != None:
        max_iter = max(len(root_url), len(new_url))
        page_number = 0
        flag = 0
        final_url = ''
        
        # If the new url is a complete url, returns the url
        if 'https:' in new_url or 'http:' in new_url:
            return new_url
        
        for i in range(max_iter):
            flag -= 1
            try:    
                # If there is a same number in the same position, it must be page number
                if int(new_url[flag]) and int(root_url[flag]) and root_url[flag] != new_url[flag]:
                    final_url = root_url[:flag] + new_url[flag:]
            except:
                continue
            finally:
                # If we find a new page number, final_url is a url for page
                if final_url:
                    return final_url
        
        # If no page number find, final_url is a url for article
        # In most of the time, there will be a duplicant '/'
        
        # thePaper's partial url does now begin with a '/'
        final_url = root_url + new_url[1:] if new_url.startswith('/') else root_url + new_url
        return final_url

def get_random_proxy():
    '''Get random proxy from proxypool
    
    Returns:
        str, proxy
    '''
    
    proxypool_url = 'http://127.0.0.1:5555/random'
    
    proxy = None
    
    try:  
        proxy = requests.get(proxypool_url).text.strip()
        print(f'Successfully get proxy: {proxy}')
    except RuntimeError as e:
        print(e)
    finally:
        return proxy
    
def test_proxy_ip(ip):
    '''Test whether proxy is available
    
    '''
    target_url = 'http://httpbin.org/get'
    proxies = {
        'http': f'http://{ip}'
    }
    try:
        requests.get(target_url, proxies=proxies, timeout=3)
    except:
        print('proxy timeout')
        return None
    
    return ip
