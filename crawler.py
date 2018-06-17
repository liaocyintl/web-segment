#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from html.parser import HTMLParser
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

SNAPSHOP_WIDTH = 1280
CHROME_BINARY_LOCATION = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
DRIVER_PATH = "driver/chromedriver.exe"


def craw_html_doc(url):
    options = Options()
    options.binary_location = CHROME_BINARY_LOCATION
    options.add_argument('--headless')
    browser = webdriver.Chrome(chrome_options=options, executable_path=DRIVER_PATH)
    browser.set_window_size(SNAPSHOP_WIDTH, 800)  # set the window size that you need
    browser.get(url)
    html = BeautifulSoup(browser.page_source, 'html.parser')
    return html


if __name__ == "__main__":
    html = craw_html_doc("https://www.yahoo.com/")
