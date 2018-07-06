#!usr/bin/env python3
# -*- coding: utf-8

"""
Test module to create threads by creating classes that inherit threading.Thread
class.
"""

__author__ = 'Ziang Lu'

import threading

import requests
from bs4 import BeautifulSoup


class MyThread(threading.Thread):
    _BASE_URL = 'https://movie.douban.com/top250?start={}&filter='

    def __init__(self, page_num: int):
        """
        Constructor with parameter.
        :param page_num: int
        """
        threading.Thread.__init__(self)
        self._page_num = page_num

    def run(self):
        # Note that run() method is automatically called when start() method is
        # called

        url = self._BASE_URL.format(self._page_num * 25)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        title_tags = soup.find('ol', class_='grid_view').find_all('li')
        for title_tag in title_tags:
            title = title_tag.find('span', class_='title').text
            print(title)


def main():
    for page_num in range(10):
        th = MyThread(page_num)
        th.start()


if __name__ == '__main__':
    main()
