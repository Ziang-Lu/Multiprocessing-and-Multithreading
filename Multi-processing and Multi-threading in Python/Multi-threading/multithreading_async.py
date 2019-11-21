#!usr/bin/env python3
# -*- coding: utf-8 -*-

"""
We can assign asynchronous tasks into a thread pool.
"""

__author__ = 'Ziang Lu'

import concurrent.futures as cf

import requests

sites = [
    'http://europe.wsj.com/',
    'http://some-made-up-domain.com/',
    'http://www.bbc.co.uk/',
    'http://www.cnn.com/',
    'http://www.foxnews.com/',
]


def site_size(url: str) -> int:
    """
    Returns the page size in bytes of the given URL.
    :param url: str
    :return: str
    """
    response = requests.get(url)
    return len(response.content)


# Create a thread pool with 10 threads
with cf.ThreadPoolExecutor(max_workers=10) as pool:
    # Submit tasks for execution
    future_to_url = {pool.submit(site_size, url): url for url in sites}
    # Wait until all the submitted tasks have been completed
    for future in cf.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            # Get the execution result
            page_size = future.result()
        except Exception as e:
            print(f'{url} generated an exception: {e}')
        else:
            print(f'{url} page is {page_size} bytes.')

# Output:
# http://some-made-up-domain.com/ generated an exception: HTTPConnectionPool(host='some-made-up-domain.com', port=80): Max retries exceeded with url: / (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x109546c90>: Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known'))
# http://www.foxnews.com/ page is 216594 bytes.
# http://www.cnn.com/ page is 1725827 bytes.
# http://europe.wsj.com/ page is 979035 bytes.
# http://www.bbc.co.uk/ page is 289252 bytes.
